use diesel::prelude::*;
use crate::schema::books;

use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize, Debug, Default, Queryable, Selectable)]
#[diesel(table_name = books)]
#[diesel(check_for_backend(diesel::pg::Pg))]
pub struct Book {
    pub isbn: String,
    pub title: String,
    pub full_title: String,
    pub authors: String,
    pub description: String,
    pub quantity: i32,
}

#[derive(Deserialize, Debug, Default, Insertable)]
#[diesel(table_name = books)]
pub struct NewBook<'a> {
    pub isbn: &'a str,
    pub title: &'a str,
    pub full_title: &'a str,
    pub authors: &'a str,
    pub description: &'a str,
}

#[derive(Deserialize, Debug, Default)]
pub struct ListOptions {
    pub offset: Option<usize>,
    pub limit: Option<usize>,
}