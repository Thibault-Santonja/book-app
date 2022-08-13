from unittest import TestCase
from server.main import is_valid_isbn


class Test(TestCase):
    def test_root(self):
        self.fail()

    def test_get_books(self):
        self.fail()

    def test_get_book(self):
        self.fail()

    def test_is_valid_isbn(self):
        self.assertTrue(is_valid_isbn("1234567890"))
        self.assertTrue(is_valid_isbn("1234567890123"))
        self.assertFalse(is_valid_isbn("123456789"))
        self.assertFalse(is_valid_isbn("123456789012"))
        self.assertFalse(is_valid_isbn("12345678901234"))
        self.assertFalse(is_valid_isbn("123456789012q"))
        self.assertFalse(is_valid_isbn("123456789q"))

    def test_get_book_details(self):
        self.fail()

    def test_get_books_in_database(self):
        self.fail()

    def test_get_book_in_database(self):
        self.fail()

    def test_insert_book_in_database(self):
        self.fail()
