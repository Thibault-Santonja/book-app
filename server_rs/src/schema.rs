// @generated automatically by Diesel CLI.

diesel::table! {
    books (isbn) {
        isbn -> Varchar,
        title -> Varchar,
        full_title -> Varchar,
        authors -> Varchar,
        description -> Varchar,
        quantity -> Integer
    }
}