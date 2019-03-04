use crate::background_task_delivery;
use crate::background_tasks::{area_db_creation, area_db_update};
use crate::Result;
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use crate::datetime_utils;

#[derive(Serialize, Deserialize, Clone)]
pub enum BackgroundTask {
    CreateAreaDatabase(String),
    UpdateAreaDatabases,
}

impl BackgroundTask {
    pub fn deliver(&self) {
        // We can at best log the errors from the async world...
        tokio::run_async(background_task_delivery::deliver(self.clone(), None));
    }

    fn deliver_after(&self, msecs: u32) {
        // We can at best log the errors from the async world...
        tokio::run_async(background_task_delivery::deliver(self.clone(), Some(msecs)));
    }

fn deliver_at(&self, when: DateTime<Utc>) {
let diff = when - Utc::now();
self.deliver_after(diff.num_milliseconds() as u32);
}

pub fn deliver_at_time(&self, hour: u32, minute: u32, second: u32) {
    self.deliver_at(datetime_utils::next_occurrence_of_time(hour, minute, second));
}

    pub fn execute(&self) -> Result<()> {
        use BackgroundTask::*;
        match self {
            CreateAreaDatabase(area_name) => area_db_creation::create_area_database(&area_name),
            UpdateAreaDatabases => area_db_update::update_area_databases(),
        }
    }
}
