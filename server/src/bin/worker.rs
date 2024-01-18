use doitlater::Worker;
use log::info;
use server::{background_tasks::ProcessOSMChangesTask, Result};

fn main() -> Result<()> {
    let _dotenv_path = dotenvy::dotenv()?;
    server::init_logging();
    let mut worker = Worker::new_from_env()?;
    info!("The worker is ready.");
    let mut scheduler = worker.create_scheduler()?;
    scheduler.register_job("process_osm_changes", "* * * * *", || {
        Box::new(ProcessOSMChangesTask)
    })?;
    worker.use_scheduler(scheduler);
        info!("Scheduled jobs registered and scheduler set, about to run worker.");
    worker.run()?;
    Ok(())
}
