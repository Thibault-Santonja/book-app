from fastapi import FastAPI
import requests
import psycopg2

import logging
import sys


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


app = FastAPI(
    title="Book App Server",
    description="Book App",
    version="0.1.0",
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/books")
async def get_books():
    return {
        "status_code": 200,
        "message": "Here your collection",
        "collection": get_books_in_database()
    }


@app.get("/books/{isbn}")
async def get_book(isbn):
    if not is_valid_isbn(isbn):
        logging.error(f"401 : Not a valid ISBN ({isbn}).")
        return {"status_code": 401, "message": "Not a valid ISBN."}

    return get_book_details(isbn)


def is_valid_isbn(isbn):
    if (len(isbn) == 10 or len(isbn) == 13) and isbn.isdigit():
        return True
    return False


def _trigger_google_api(json_response):
    book_info = json_response["items"][0]["volumeInfo"]
    return {
        "title": book_info.get("title"),
        "full_title": None,
        #"isbn_10": book_info["industryIdentifiers"][0]["identifier"],
        #"isbn_13": book_info["industryIdentifiers"][1]["identifier"],
        "authors": ', '.join(book_info.get("authors", [])),
        "description": book_info.get("description")
    }


def _trigger_open_library(book_info):
    return {
        "title": book_info.get("title"),
        "full_title": book_info.get("full_title"),
        #"isbn_10": book_info.get("isbn_10", [None])[0],
        #"isbn_13": book_info.get("isbn_13", [None])[0],
        "authors": None,
        "description": None
    }


def extract_book_details(json_response, origin_api):
    response_handler = {
        "googleapi": _trigger_google_api,
        "openlibrary": _trigger_open_library
    }
    action_handler = response_handler.get(origin_api)
    return action_handler(json_response)


def _trigger_ok(response, isbn, origin_api):
    book = extract_book_details(response.json(), origin_api)
    logging.info(f"{response.status_code} : Book found on {origin_api} : {book}.")
    insert_book_in_database(isbn, book)
    return {"is_valid": True, "result": book}


def _trigger_not_found(response, isbn, origin_api):
    logging.info(f"{response.status_code} : Book not found on {origin_api} ({isbn}).")
    return {"is_valid": False, "result": {"status_code": 404, "message": f"Book not found."}}


def _trigger_server_error(response, isbn, origin_api):
    logging.info(f"{response.status_code} : Server error on {origin_api} ({isbn}).") 
    return {"is_valid": False, "result": {"status_code": 500, "message": f"Server error."}}


def _trigger_server_unknown(response, isbn, origin_api):
    logging.info(f"{response.status_code} : Unknow error for {isbn} from {origin_api} :\n{response.json()}") 
    return {"is_valid": False, "result": {"status_code": response.status_code, "message": f"Unknow error."}}


def handle_code_response(response, isbn, origin_api):
    response_handler = {
        200: _trigger_ok,
        404: _trigger_not_found,
        500: _trigger_server_error
    }
    action_handler = response_handler.get(response.status_code, _trigger_server_unknown)
    return action_handler(response, isbn, origin_api)


def is_response_contains_items(response):
    if response.json()["totalItems"] < 1:
        return False
    return True


def try_query_api(url: str):
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectTimeout:
        response = {"status_code": 500, "message": "Connection timeout"}
    return response


def get_book_in_open_library(isbn: str) -> dict:
    response = try_query_api(f"https://openlibrary.org/isbn/{isbn}.json")
    return handle_code_response(response, isbn, "openlibrary")


def get_book_in_google_api(isbn: str) -> dict:
    response = try_query_api(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")
    if not is_response_contains_items(response):
        response.status_code = 404
    return handle_code_response(response, isbn, "googleapi")


def get_book_details(isbn):
    book = get_book_in_database(isbn)

    if not book:
        response = get_book_in_google_api(isbn)
        book = response["result"]
        
        if not response["is_valid"]:
            response = get_book_in_open_library(isbn)
            book = response["result"]

            if not response["is_valid"]:
                return response["result"]
        
    title =  book.get('title')
    full_title = book.get('full_title')

    return {
        "status_code": 200,
        "message": "Your book is found",
        "isbn": isbn,
        "title": full_title if full_title else title
    }


def get_books_in_database(many=None):
    conn = None
    try:
        conn = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="127.0.0.1",
            port="5432",
            database="library"
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM books;")
            if many:
                res = cursor.fetchmany(many)
            else:
                res = cursor.fetchall()
            return {
                "columns": [desc[0] for desc in cursor.description],
                "data": res
            }
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        if conn is not None:
            conn.close()


def get_book_in_database(isbn):
    conn = None
    try:
        conn = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="127.0.0.1",
            port="5432",
            database="library"
        )
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM books WHERE isbn='{isbn}';")
            res = cursor.fetchone()
            if res:
                res = dict(zip([desc[0] for desc in cursor.description], res))
                if is_not_null(res['authors']) and is_not_null(res['description']):
                    logging.info(f"book found in database {res}")
                    return res
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        if conn is not None:
            conn.close()

def is_not_null(text):
    return text not in (None, 'None', '')


def format_text_for_database(text):
    if is_not_null(text):
        text = text.replace("'", "''")
        return f"'{text}'"
    return "NULL"


def insert_book_in_database(isbn, book_details):
    conn = None
    try:
        conn = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="127.0.0.1",
            port="5432",
            database="library"
        )
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO books(isbn, title, full_title, authors, description)
            VALUES ({format_text_for_database(isbn)},{format_text_for_database(book_details['title'])},{format_text_for_database(book_details.get('full_title'))},{format_text_for_database(book_details.get('authors'))},{format_text_for_database(book_details.get('description'))}) 
            ON CONFLICT (isbn) DO UPDATE SET
                title = COALESCE(EXCLUDED.title, books.title),
                full_title = COALESCE(EXCLUDED.full_title, books.full_title),
                authors = COALESCE(EXCLUDED.authors, books.authors),
                description = COALESCE(EXCLUDED.description, books.description)
            RETURNING isbn;
        """)
        conn.commit()
        cursor.close()
        logging.info(f"isbn/{isbn} ({book_details.get('title')}) : Book inserted in database.")
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"isbn/{isbn} ({book_details.get('title')}) : Fail to insert book in database : {error}")
    finally:
        if conn is not None:
            conn.close()
