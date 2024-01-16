use osm_api::replication::ReplicationApiClient;
use osm_api::replication::SequenceNumber;
use server::{Result, db::{self, InsertableChangeset}};
use std::env;

fn main() -> Result<()> {
    let initial_batch: u32 = env::args().nth(1).unwrap().parse().expect("Initial batch must be a number.");
    let client = ReplicationApiClient::default();
    let latest_state = client.latest_changesets_replication_state()?;
    let conn = db::connect_to_server_db()?;
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
        println!("Inserted {} changesets from changesets batch {}.", num_changesets, batch);
    }
    println!("Done.");
    Ok(())
}