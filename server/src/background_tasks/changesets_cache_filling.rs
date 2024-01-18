use crate::{Result, db::{self, InsertableChangeset}};
use doitlater::typetag;
use log::info;
use osm_api::replication::ReplicationApiClient;
use osm_api::replication::SequenceNumber;
use serde::{Deserialize, Serialize};
use super::state_tracking;

const STATE_FILE: &str = "latest_processed_changesets.sn";

#[derive(Serialize, Deserialize)]
pub struct ChangesetsCacheFillingTask;

#[typetag::serde]
impl doitlater::Executable for ChangesetsCacheFillingTask {
    fn execute(&self) -> std::result::Result<(), Box<dyn std::error::Error>> {
        fill_cache_with_missing_changesets().map_err(|e| Box::new(e) as Box<dyn std::error::Error>)
    }
}

fn fill_cache_with_missing_changesets() -> Result<()> {
    let initial_batch = state_tracking::read_latest_sequence_number(STATE_FILE, 5_790_000)?;
    let client = ReplicationApiClient::default();
    let latest_state = client.latest_changesets_replication_state()?;
    let conn = db::connect_to_server_db()?;
    info!("Filling changesets cache with changesets from batches from {} to {}.", initial_batch, latest_state.sequence_number.0);
    for batch in initial_batch..=latest_state.sequence_number.0 {
        let changesets = client.get_changesets(SequenceNumber(batch))?;
        let num_changesets = changesets.len();
        for api_changeset in changesets {
            if api_changeset.bounds.is_none() {
                continue; // We don't need changesets without bounds, they will never appear as a changeset of a change.
            }
            let changeset = InsertableChangeset::from(api_changeset);
            db::insert_or_update_changeset(&conn, &changeset, batch)?;
        }
        info!("Inserted {} changesets from changesets batch {}.", num_changesets, batch);
    }
    state_tracking::save_latest_sequence_number(STATE_FILE, latest_state.sequence_number.0)?;
    info!("Finished filling changesets cache.");
    Ok(())
}