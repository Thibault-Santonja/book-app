from fastapi import FastAPI
import requests
import psycopg2

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
        print("401 : Not a valid ISBN.")  # FIXME: DEBUG
        return {"status_code": 401, "message": "Not a valid ISBN."}

    return get_book_details(isbn)


def is_valid_isbn(isbn):
    if (len(isbn) == 10 or len(isbn) == 13) and isbn.isdigit():
        return True
    return False


def get_book_details(isbn):
    book = get_book_in_database(isbn)
    if not book:
        result = requests.get(f"https://openlibrary.org/isbn/{isbn}.json")

        if result.status_code == 404:
            print("404 : Book not found.")  # FIXME: DEBUG
            return {"status_code": 404, "message": "Book not found."}

        book = result.json()
        insert_book_in_database(isbn, book)
    return {
        "status_code": 200,
        "message": "Your book is found",
        "isbn": isbn,
        "title": book.get('full_title', book.get('title'))
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
                res =  cursor.fetchall()
            return {
                "columns": [desc[0] for desc in cursor.description],
                "data": res
            }
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
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
                return dict(zip([desc[0] for desc in cursor.description], res))
            else:
                None
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


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
            INSERT INTO books(isbn, title, full_title)
            VALUES ('{isbn}','{book_details['title']}','{book_details.get('full_title')}')
            RETURNING isbn;
        """)
        conn.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
