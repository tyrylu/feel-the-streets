use rocket::fairing::AdHoc;
use rocket::fs::FileServer;
use rocket::routes;
use rocket_dyn_templates::Template;
use server::api_routes;
use server::ui_routes;
use server::DbConn;

#[rocket::launch]
fn rocket() -> _ {
    let _dotenv_path = dotenv::dotenv().expect("Failed to setup environment from env file");
    server::init_logging();
    rocket::build()
        .attach(DbConn::fairing())
        .attach(AdHoc::on_liftoff("Database Migrations", |rocket| {
            Box::pin(async move {
                let conn = DbConn::get_one(rocket).await.expect("database connection");
                match conn.run(|c| server::run_migrations(c)).await {
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
                api_routes::areas,
                api_routes::maybe_create_area,
                api_routes::download_area,
                api_routes::ping,
                api_routes::motd,
                api_routes::create_client,
            ],
        )
        .mount("/", routes![ui_routes::areas, ui_routes::area_detail])
        .mount("/", FileServer::from("static"))
        .attach(Template::fairing())
}
