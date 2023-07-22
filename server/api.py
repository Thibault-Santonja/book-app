from fastapi import APIRouter

from models import Book
from crud import get_book_details, list_books, update_book, create_book

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

router = APIRouter()


@router.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


@router.get("/books")
async def get_books(limit: int | None = None, offset: int | None = None):
    if limit and limit < 0:
        return {
            "status_code": 401,
            "message": "Limit must be greater than zero"
        }
    if offset and offset < 0:
        return {
            "status_code": 401,
            "message": "Offset must be greater than zero"
        }
    return {
        "status_code": 200,
        "message": "Here your collection",
        "collection": list_books(limit, offset)
    }


@router.get("/books/{isbn}")
async def get_book(isbn: str) -> Book | dict:
    if not is_valid_isbn(isbn):
        return _not_valid_isbn(isbn)

    return get_book_details(isbn)


@router.post("/books/")
async def post_book(book: Book) -> Book | dict:
    if not is_valid_isbn(book.get_isbn()):
        return _not_valid_isbn(book.get_isbn())

    return create_book(book)


@router.put("/books/{isbn}", response_model=Book | dict)
async def put_book(isbn: str, book: Book) -> Book | dict:
    if not is_valid_isbn(isbn):
        return _not_valid_isbn(isbn)

    return update_book(isbn, book)


def is_valid_isbn(isbn: str) -> bool:
    if (len(isbn) == 10 or len(isbn) == 13) and isbn.isdigit():
        return True
    return False

def _not_valid_isbn(isbn: str) -> dict:
    logging.error(f"401 : Not a valid ISBN ({isbn}).")
    return {"status_code": 401, "message": "Not a valid ISBN."}
