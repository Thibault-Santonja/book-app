create table books
(
    isbn          text                    not null
        constraint books_pk
            primary key,
    title         text,
    isbn_10       text,
    isbn_13       text,
    quantity      integer,
    full_title    text,
    date_inserted timestamp default now() not null,
    date_updated  timestamp default now() not null
);

create unique index books_isbn_10_uindex
    on books (isbn_10);

create unique index books_isbn_13_uindex
    on books (isbn_13);

create unique index books_isbn_uindex
    on books (isbn);