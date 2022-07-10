from fastapi import FastAPI
import requests

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

    print(f"200 : {book_details['title']}")  # FIXME: DEBUG
    print(book_details) # FIXME: DEBUG

    return {"status_code": 200, "message": "Your book is found",
        "isbn": isbn, "title": book_details["title"]}

def get_book_details(isbn):
    return requests.get(f"https://openlibrary.org/isbn/{isbn}.json")

def is_valid_isbn(isbn):
    if (len(isbn) == 10 or len(isbn) == 13) and isbn.isdigit():
        return True
    return False
