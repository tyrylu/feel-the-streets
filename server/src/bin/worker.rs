use doitlater::Worker;
use log::info;
use server::{background_tasks::UpdateAreaDatabasesTask, Result};

fn main() -> Result<()> {
    let _dotenv_path = dotenv::dotenv()?;
    server::init_logging();
    let mut worker = Worker::new_from_env()?;
    info!("The worker is ready.");
    let mut scheduler = worker.create_scheduler()?;
    scheduler.register_job("update_area_databases", "57 23 * * *", || {
        Box::new(UpdateAreaDatabasesTask)
    })?;
    worker.use_scheduler(scheduler);
    info!("Scheduled jobs registered and scheduler set, about to run worker.");
    worker.run()?;
    Ok(())
}
