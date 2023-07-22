import psycopg2

from models import Book

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

def get_books_in_database(limit: int|None, offset: int|None, many: int|None = None) -> dict:
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
            query = "SELECT * FROM books ORDER BY title"
            if limit:
                query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
            query += ";"
            cursor.execute(query)
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


def get_book_in_database(isbn: str) -> dict:
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
                    return Book(isbn = res['isbn'], title = res['title'], authors = res['authors'], description = res['description'], full_title = res['full_title'], quantity = res['quantity'])
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        if conn is not None:
            conn.close()

def is_not_null(text: str) -> bool:
    return text not in (None, 'None', '')


def format_text_for_database(text: str) -> str:
    if is_not_null(text):
        text = text.replace("'", "''")
        return f"'{text}'"
    return "NULL"


def insert_book_in_database(isbn: str, book: Book) -> None:
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
            INSERT INTO books(isbn, title, full_title, authors, description, quantity)
            VALUES ({format_text_for_database(isbn)},{format_text_for_database(book.get_title())},{format_text_for_database(book.get_full_title())},{format_text_for_database(book.get_authors())},{format_text_for_database(book.get_description())},1) 
            ON CONFLICT (isbn) DO UPDATE SET
                title = COALESCE(EXCLUDED.title, books.title),
                full_title = COALESCE(EXCLUDED.full_title, books.full_title),
                authors = COALESCE(EXCLUDED.authors, books.authors),
                description = COALESCE(EXCLUDED.description, books.description),
                quantity = COALESCE(EXCLUDED.quantity, books.quantity)
            RETURNING isbn;
        """)
        conn.commit()
        cursor.close()
        logging.info(f"isbn/{isbn} ({book.get_title()}) : Book inserted in database.")
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"isbn/{isbn} ({book.get_title()}) : Fail to insert book in database : {error}")
    finally:
        if conn is not None:
            conn.close()

def update_book_in_database(isbn: str, book: Book) -> Book:
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
            UPDATE books
                SET title = COALESCE({format_text_for_database(book.get_title())}, title),
                    full_title = COALESCE({format_text_for_database(book.get_full_title())}, full_title),
                    authors = COALESCE({format_text_for_database(book.get_authors())}, authors),
                    description = COALESCE({format_text_for_database(book.get_description())}, description)
                WHERE isbn='{isbn}'
                RETURNING *;
        """)
        conn.commit()
        cursor.close()
        logging.info(f"isbn/{isbn} ({book.get_title()}) : Book updated in database.")
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"isbn/{isbn} ({book.get_title()}) : Fail to update book in database : {error}")
    finally:
        if conn is not None:
            conn.close()
