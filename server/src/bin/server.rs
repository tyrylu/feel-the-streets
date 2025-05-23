use axum::Router;
use server::api_routes;
use server::db;
use server::ui_routes;
use server::{AppState, Result};
use std::sync::{Arc, Mutex};
use tera::Tera;
use tokio::net::TcpListener;
use tower_http::services::ServeDir;
use tower_http::trace::TraceLayer;

#[tokio::main]
async fn main() -> Result<()> {
    let _dotenv_path = dotenvy::dotenv().expect("Failed to setup environment from env file");
    server::init_logging();
    let tera = Tera::new("templates/*")?;
    let db_conn = Arc::new(Mutex::new(db::connect_to_server_db()?));
    let state = AppState {
        templates: tera,
        db_conn,
    };
    let app = Router::new()
        .nest_service("/static", ServeDir::new("static"))
        .nest("/api", api_routes::routes())
        .merge(ui_routes::routes())
        .layer(TraceLayer::new_for_http())
        .with_state(state);
    let addr = "127.0.0.1:8000";
    log::info!("Listening on {}", addr);
    let listener = TcpListener::bind(addr).await?;
    axum::serve(listener, app.into_make_service()).await?;
    Ok(())
}
