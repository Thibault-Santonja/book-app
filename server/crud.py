import requests

from models import Book
from db import insert_book_in_database, get_book_in_database, get_books_in_database, update_book_in_database

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

def _trigger_google_api(json_response: dict, isbn: str) -> Book:
    book_info = json_response["items"][0]["volumeInfo"]
    return Book(
        isbn = isbn,
        title = book_info.get("title"),
        #"isbn_10": book_info["industryIdentifiers"][0]["identifier"],
        #"isbn_13": book_info["industryIdentifiers"][1]["identifier"],
        authors = ', '.join(book_info.get("authors", [])),
        description = book_info.get("description")
    )


def _trigger_open_library(book_info: dict, isbn: str) -> Book:
    return Book(
        isbn = isbn,
        title = book_info.get("title"),
        full_title = book_info.get("full_title"),
        #"isbn_10": book_info.get("isbn_10", [None])[0],
        #"isbn_13": book_info.get("isbn_13", [None])[0],
        #authors = ', '.join(book_info.get("authors", [])),
        description = book_info.get("description")
    )


def extract_book_details(json_response: dict, origin_api: str, isbn: str) -> Book:
    response_handler = {
        "googleapi": _trigger_google_api,
        "openlibrary": _trigger_open_library
    }
    action_handler = response_handler.get(origin_api)
    return action_handler(json_response, isbn)


def _trigger_ok(response: dict, isbn: str, origin_api: str) -> dict:
    book = extract_book_details(response.json(), origin_api, isbn)
    logging.info(f"{response.status_code} : Book found on {origin_api} : {book}.")
    insert_book_in_database(isbn, book)
    return {"is_valid": True, "result": book}


def _trigger_not_found(response: dict, isbn: str, origin_api: str) -> dict:
    logging.info(f"{response.status_code} : Book not found on {origin_api} ({isbn}).")
    return {"is_valid": False, "result": {"status_code": 404, "message": "Book not found."}}


def _trigger_server_error(response: dict, isbn: str, origin_api: str) -> dict:
    logging.info(f"{response.status_code} : Server error on {origin_api} ({isbn}).") 
    return {"is_valid": False, "result": {"status_code": 500, "message": "Server error."}}


def _trigger_server_unknown(response: dict, isbn: str, origin_api: str) -> dict:
    logging.info(f"{response.status_code} : Unknow error for {isbn} from {origin_api} :\n{response.json()}") 
    return {"is_valid": False, "result": {"status_code": response.status_code, "message": "Unknow error."}}


def handle_code_response(response: dict, isbn: str, origin_api: str) -> dict:
    response_handler = {
        200: _trigger_ok,
        404: _trigger_not_found,
        500: _trigger_server_error
    }
    action_handler = response_handler.get(response.status_code, _trigger_server_unknown)
    return action_handler(response, isbn, origin_api)
def is_response_contains_items(response: dict) -> bool:
    if response.json()["totalItems"] < 1:
        return False
    return True


def try_query_api(url: str) -> dict:
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


def get_book_details(isbn: str) -> dict:
    book = get_book_in_database(isbn)

    if not book:
        response = get_book_in_google_api(isbn)
        book = response["result"]
        
        if not response["is_valid"]:
            response = get_book_in_open_library(isbn)
            book = response["result"]

            if not response["is_valid"]:
                return response["result"]
        
    title =  book.get_title()
    full_title = book.get_full_title()

    return {
        "status_code": 200,
        "message": "Your book is found",
        "isbn": isbn,
        "title": full_title if full_title else title
    }


def list_books(limit: str | int, offset: str | int) -> dict:
    return get_books_in_database(limit, offset)


def create_book(book: Book) -> Book:
    insert_book_in_database(book.get_isbn(), book)
    return {"is_valid": True, "result": book}


def update_book(isbn: str, book: Book) -> Book:
    update_book_in_database(isbn, book)
    return {"is_valid": True, "result": book}
