use crate::background_task_delivery;
use crate::background_tasks::{area_db_creation, area_db_update};
use crate::Result;
use serde::{Deserialize, Serialize};
use tokio;

#[derive(Serialize, Deserialize, Clone)]
pub enum BackgroundTask {
    CreateAreaDatabase(String),
    UpdateAreaDatabases,
}

impl BackgroundTask {
    pub fn deliver(&self) {
        // We can at best log the errors from the async world...
        tokio::run_async(background_task_delivery::deliver(self.clone()));
    }

    pub fn execute(&self) -> Result<()> {
        use BackgroundTask::*;
        match self {
            CreateAreaDatabase(area_name) => area_db_creation::create_area_database(&area_name),
            UpdateAreaDatabases => area_db_update::update_area_databases(),
        }
    }
}
