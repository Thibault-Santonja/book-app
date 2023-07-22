pub mod models;
pub mod schema;
use self::schema::books;
use self::models::Book;
use self::models::ListOptions;
//use self::schema::books::dsl::*;

use diesel::pg::PgConnection;
use diesel::prelude::*;
use diesel::r2d2::{ConnectionManager, Pool, PoolError, PooledConnection};
use once_cell::sync::OnceCell;
use salvo::prelude::*;

const DB_URL: &str = "postgres://benchmarkdbuser:benchmarkdbpass@tfb-database/hello_world";
type PgPool = Pool<ConnectionManager<PgConnection>>;

static DB_POOL: OnceCell<PgPool> = OnceCell::new();

fn connect() -> Result<PooledConnection<ConnectionManager<PgConnection>>, PoolError> {
    DB_POOL.get().unwrap().get()
}

fn build_pool(database_url: &str, size: u32) -> Result<PgPool, PoolError> {
    let manager = ConnectionManager::<PgConnection>::new(database_url);
    diesel::r2d2::Pool::builder()
        .max_size(size)
        .min_idle(Some(size))
        .test_on_check_out(false)
        .idle_timeout(None)
        .max_lifetime(None)
        .build(manager)
}

#[tokio::main]
async fn main() {
    DB_POOL
        .set(build_pool(&DB_URL, 10).expect(&format!("Error connecting to {}", &DB_URL)))
        .ok();

    tracing_subscriber::fmt().init();
    start_server().await;
}

pub(crate) async fn start_server() {
    let acceptor = TcpListener::new("127.0.0.1:5800").bind().await;
    Server::new(acceptor).serve(route()).await;
}

fn route() -> Router {
    Router::with_path("books")
        .post(create_book)
        .get(list_books)
        .push(Router::with_path("<isbn>")
            .get(get_book)
            .put(update_book)
            .delete(delete_book)
        )
}

#[handler]
async fn hello() -> &'static str {
    "Hello World"
}

#[handler]
pub async fn get_book(req: &mut Request, res: &mut Response) {
    // use self::schema::books::dsl::books;
    let isbn = req.param::<String>("isbn").unwrap();
    tracing::debug!(isbn = ?isbn, "get book");

    // `find()` doc https://docs.diesel.rs/2.0.x/diesel/query_dsl/trait.QueryDsl.html#method.find
    let conn = connect();
    let book_result: Book = books::table.find(isbn).first::<Book>(&conn);
    tracing::debug!(book_result = ?book_result, "get book");
    
    res.render(Json("bite"));
}

#[handler]
pub async fn list_books(req: &mut Request, res: &mut Response) {
    let opts = req.parse_body::<ListOptions>().await.unwrap_or_default();
    tracing::debug!(opts = ?opts, "list books");

    // `get_result` doc https://docs.diesel.rs/2.0.x/diesel/prelude/trait.RunQueryDsl.html#method.get_results
    let conn = connect();
    let books_res: Vec<Book> = books::table
        .offset(0)
        .limit(100)
        .get_results::<Book>(&conn);
    
    res.render(Json(books_res));
}

#[handler]
pub async fn create_book(req: &mut Request, res: &mut Response) {
    let new_book = req.parse_body::<Book>().await.unwrap();
    tracing::debug!(book = ?new_book, "create book");
    
    res.status_code(StatusCode::CREATED);
}

#[handler]
pub async fn update_book(req: &mut Request, res: &mut Response) {
    let isbn: String = req.param::<String>("isbn").unwrap();
    let book = req.parse_body::<Book>().await.unwrap();
    tracing::debug!(book = ?book, isbn = ?isbn, "update book");
    
    res.status_code(StatusCode::OK);
}

#[handler]
pub async fn delete_book(req: &mut Request, res: &mut Response) {
    let isbn: String = req.param::<String>("isbn").unwrap();
    tracing::debug!(isbn = ?isbn, "delete book");
    
    res.status_code(StatusCode::NO_CONTENT);
}