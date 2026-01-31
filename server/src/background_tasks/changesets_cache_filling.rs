use super::state_tracking;
use crate::{
    db::{self, InsertableChangeset},
    Result,
};
use log::info;
use osm_api::replication::ReplicationApiClient;
use osm_api::replication::SequenceNumber;

const STATE_FILE: &str = "latest_processed_changesets.sn";

pub(crate) fn fill_cache_with_missing_changesets(
    client: &ReplicationApiClient,
    to_batch: SequenceNumber,
) -> Result<()> {
    let initial_batch = state_tracking::read_latest_sequence_number(STATE_FILE, 5_790_000)?;
    let conn = db::connect_to_server_db()?;
    info!(
        "Filling changesets cache with changesets from batches from {} to {}.",
        initial_batch, to_batch.0
    );
    for batch in initial_batch..=to_batch.0 {
        let changesets = client.get_changesets(SequenceNumber(batch))?;
        let num_changesets = changesets.len();
        for api_changeset in changesets {
            if api_changeset.bounds.is_none() {
                continue; // We don't need changesets without bounds, they will never appear as a changeset of a change.
            }
            let changeset = InsertableChangeset::from(api_changeset);
            db::insert_or_update_changeset(&conn, &changeset, batch)?;
        }
        state_tracking::save_latest_sequence_number(STATE_FILE, batch)?;
        info!(
            "Inserted {} changesets from changesets batch {}.",
            num_changesets, batch
        );
    }
    info!("Finished filling changesets cache.");
    Ok(())
}
