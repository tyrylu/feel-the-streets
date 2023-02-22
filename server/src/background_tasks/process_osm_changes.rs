use crate::Result;
use doitlater::typetag;
use osm_api::replication::{ReplicationApiClient, SequenceNumber};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct ProcessOSMChangesTask;

#[typetag::serde]
impl doitlater::Executable for ProcessOSMChangesTask {
    fn execute(&self) -> std::result::Result<(), Box<dyn std::error::Error>> {
        run_osm_changes_processing().map_err(|e| Box::new(e) as Box<dyn std::error::Error>)
    }
}

fn run_osm_changes_processing() -> Result<()> {
    info!("Starting periodic OSM change processing.");
    let initial_sn = 5_000_000;
    process_osm_changes(initial_sn)?;
    Ok(())
}

fn process_osm_changes(initial_sn: u32) -> Result<()> {
    let r_client = ReplicationApiClient::default();
    let latest_state = r_client.latest_replication_state()?;
    info!(
        "Processing OSM changes from {initial_sn} to {}",
        latest_state.sequence_number.0
    );
    for sn in initial_sn..=latest_state.sequence_number.0 {
        process_osm_change(sn, &r_client)?;
    }
    Ok(())
}

fn process_osm_change(sn: u32, r_client: &ReplicationApiClient) -> Result<()> {
    debug!("Processing OSM change {sn}.");
    let _change = r_client.get_change(SequenceNumber::from_u32(sn)?)?;
    Ok(())
}
