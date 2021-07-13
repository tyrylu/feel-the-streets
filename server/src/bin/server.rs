use rocket::fairing::AdHoc;
use rocket::routes;
use server::routes;
use server::DbConn;

#[rocket::launch]
fn rocket() -> _ {
    let _dotenv_path = dotenv::dotenv().expect("Failed to setup environment from env file");
    server::init_logging();
        rocket::build()
        .attach(DbConn::fairing())
        .attach(AdHoc::on_liftoff("Database Migrations", |rocket| {
            Box::pin(async move {
                let conn = DbConn::get_one(&rocket).await.expect("database connection");
                match conn.run(|c| server::run_migrations(&c)).await {
                    Ok(()) => (),
                    Err(e) => {
                        panic!("Failed to run database migrations: {:?}", e);
                    }
                }
            })
        }))
        .mount(
            "/api",
            routes![
                routes::areas,
                routes::maybe_create_area,
                routes::download_area,
                routes::ping,
                routes::motd,
                routes::create_client,
            ],
        )
}
