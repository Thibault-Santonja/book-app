pub mod models;
pub mod schema;

use diesel::prelude::*;
use dotenvy::dotenv;
use std::env;

use self::models::{NewBook, Book};

pub fn establish_connection() -> PgConnection {
    dotenv().ok();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    PgConnection::establish(&database_url)
        .unwrap_or_else(|_| panic!("Error connecting to {}", database_url))
}

pub fn create_book(conn: &mut PgConnection, isbn: &str, title: &str, full_title: &str, authors: &str, description: &str) -> Book {
    use crate::schema::books;

    let new_book = NewBook { isbn, title, full_title, authors, description };

    diesel::insert_into(books::table)
        .values(&new_book)
        .returning(Book::as_returning())
        .get_result(conn)
        .expect("Error saving new book")
}