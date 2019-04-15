// Rocket related stuff
#![feature(proc_macro_hygiene, decl_macro)]

use log::error;
use rocket::fairing::AdHoc;
use rocket::routes;
use server::routes;
use server::{DbConn, Result};

fn main() -> Result<()> {
    server::init_logging();
    let _dotenv_path = dotenv::dotenv()?;
    rocket::ignite()
        .attach(DbConn::fairing())
        .attach(AdHoc::on_attach("Database Migrations", |rocket| {
            let conn = DbConn::get_one(&rocket).expect("database connection");
            match server::run_migrations(&*conn) {
                Ok(()) => Ok(rocket),
                Err(e) => {
                    error!("Failed to run database migrations: {:?}", e);
                    Err(rocket)
                }
            }
        }))
        .mount(
            "/api",
            routes![
                routes::areas,
                routes::maybe_create_area,
                routes::download_area,
                routes::ping
            ],
        )
        .launch();
    Ok(())
}
