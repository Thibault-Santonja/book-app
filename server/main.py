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

@app.get("/books/{isbn}")
async def post_isbn(isbn):
    if not is_valid_isbn(isbn):
        print("401 : Not a valid ISBN.")  # FIXME: DEBUG
        return {"status_code": 401, "message": "Not a valid ISBN."}

    result = get_book_details(isbn)
    if result.status_code == 404:
        print("404 : Book not found.")  # FIXME: DEBUG
        return {"status_code": 404, "message": "Book not found."}

    book_details = result.json()

    print(f"200 : {book_details.get('full_title')}")  # FIXME: DEBUG
    print(book_details) # FIXME: DEBUG

    insert_book_in_database(isbn, book_details)

    return {"status_code": 200, "message": "Your book is found",
        "isbn": isbn, "title": book_details.get('full_title', book_details.get('title'))}

def get_book_details(isbn):
    return requests.get(f"https://openlibrary.org/isbn/{isbn}.json")

def is_valid_isbn(isbn):
    if (len(isbn) == 10 or len(isbn) == 13) and isbn.isdigit():
        return True
    return False

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
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO books(isbn, title, full_title)
            VALUES ('{isbn}','{book_details['title']}','{book_details.get('full_title')}')
            RETURNING isbn;
        """)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()