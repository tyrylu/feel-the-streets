use axum::Router;
use server::{AppState, Result};
use server::api_routes;
use server::ui_routes;
use tera::Tera;
use diesel::{Connection, SqliteConnection};
use std::net::SocketAddr;
use std::sync::{Arc, Mutex};

#[tokio::main]
async fn main() -> Result<()> {
    let _dotenv_path = dotenvy::dotenv().expect("Failed to setup environment from env file");
    server::init_logging();
    let tera = Tera::new("templates/*")?;
    let db_conn = Arc::new(Mutex::new(SqliteConnection::establish("server.db")?));
    server::run_migrations(&mut db_conn.lock().unwrap())?;
    let state = AppState { templates: tera, db_conn };
    let app = Router::new()
    .nest("/api", api_routes::routes())
    .nest("/", ui_routes::routes())
    .with_state(state);
    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await.unwrap();
Ok(())
    }
