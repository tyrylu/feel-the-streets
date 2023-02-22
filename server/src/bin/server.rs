use axum::Router;
use axum_extra::routing::SpaRouter;
use server::api_routes;
use server::db;
use server::ui_routes;
use server::{AppState, Result};
use std::net::SocketAddr;
use std::sync::{Arc, Mutex};
use tera::Tera;
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
    let spa = SpaRouter::new("/static", "static");
    let app = Router::new()
        .merge(spa)
        .nest("/api", api_routes::routes())
        .nest("/", ui_routes::routes())
        .layer(TraceLayer::new_for_http())
        .with_state(state);
    let addr = SocketAddr::from(([127, 0, 0, 1], 8000));
    log::info!("Listening on {}", addr);
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
    Ok(())
}
