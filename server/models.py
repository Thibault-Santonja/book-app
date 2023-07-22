from pydantic import BaseModel


class Book(BaseModel):
    isbn: str
    title: str | None = None
    full_title: str | None = None
    authors: str | None = None
    description: str | None = None
    quantity: int = 1

    def __str__(self) -> str:
        return f"{self.title} written by {self.authors} (isbn: {self.isbn})"

    def get_isbn(self):
        return self.isbn

    def get_title(self):
        return self.title

    def get_full_title(self):
        return self.full_title

    def get_authors(self):
        return self.authors

    def get_description(self):
        return self.description