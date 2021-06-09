use crate::background_task_constants;
use crate::background_task_delivery;
use crate::background_tasks::{area_db_creation, area_db_update};
use crate::datetime_utils;
use crate::Result;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone)]
pub enum BackgroundTask {
    CreateAreaDatabase(i64),
    UpdateAreaDatabases,
}

impl BackgroundTask {
    pub fn deliver(&self) -> Result<()> {
        background_task_delivery::deliver(self, None)
    }

    fn deliver_after(&self, msecs: u32) -> Result<()> {
        background_task_delivery::deliver(self, Some(msecs))
    }

    pub fn deliver_at_time(&self, hour: u32, minute: u32, second: u32) -> Result<()> {
        self.deliver_after(datetime_utils::compute_ttl_for_time(hour, minute, second))
    }

    pub fn execute(&self) -> Result<()> {
        use BackgroundTask::*;
        match self {
            CreateAreaDatabase(area_osm_id) => area_db_creation::create_area_database(*area_osm_id),
            UpdateAreaDatabases => area_db_update::update_area_databases(),
        }
    }

    pub fn get_next_schedule_time(&self) -> Option<(u32, u32, u32)> {
        use background_task_constants::*;
        match self {
            BackgroundTask::UpdateAreaDatabases => Some((
                DATABASES_UPDATE_HOUR,
                DATABASES_UPDATE_MINUTE,
                DATABASES_UPDATE_SECOND,
            )),
            _ => None,
        }
    }
}
