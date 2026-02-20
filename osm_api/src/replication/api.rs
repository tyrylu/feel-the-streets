use super::change::RawOSMChanges;
use super::{OSMChanges, ReplicationState, SequenceNumber};
use crate::changeset::Changeset;
use crate::raw_changeset::RawChangesets;
use crate::Result;
use flate2::read::GzDecoder;
use std::io::BufReader;
use ureq::{config::Config, Agent};

const PLANET_REPLICATION_BASE: &str = "https://planet.openstreetmap.org/replication";

pub struct ReplicationApiClient {
    agent: Agent,
}

impl ReplicationApiClient {
    pub fn latest_changes_replication_state(&self) -> Result<ReplicationState> {
        Ok(ReplicationState::from_changes_state_str(
            &self
                .agent
                .get(&format!("{PLANET_REPLICATION_BASE}/minute/state.txt"))
                .call()?
                .into_body()
                .read_to_string()?,
        )?)
    }

    pub fn get_change(&self, number: SequenceNumber) -> Result<OSMChanges> {
        let changes: RawOSMChanges = quick_xml::de::from_reader(BufReader::new(GzDecoder::new(
            self.agent
                .get(&format!(
                    "{PLANET_REPLICATION_BASE}/minute/{}",
                    number.data_path()
                ))
                .call()?
                .into_body()
                .into_reader(),
        )))?;
        changes.try_into()
    }

    pub fn get_changes_batch_info(&self, number: &SequenceNumber) -> Result<ReplicationState> {
        Ok(ReplicationState::from_changes_state_str(
            &self
                .agent
                .get(&format!(
                    "{PLANET_REPLICATION_BASE}/minute/{}",
                    number.state_path()
                ))
                .call()?
                .into_body()
                .read_to_string()?,
        )?)
    }

    pub fn latest_changesets_replication_state(&self) -> Result<ReplicationState> {
        Ok(ReplicationState::from_changesets_state_str(
            &self
                .agent
                .get(&format!("{PLANET_REPLICATION_BASE}/changesets/state.yaml"))
                .call()?
                .into_body()
                .read_to_string()?,
        )?)
    }

    pub fn get_changesets(&self, number: SequenceNumber) -> Result<Vec<Changeset>> {
        let changes: RawChangesets = quick_xml::de::from_reader(BufReader::with_capacity(1024*1024, GzDecoder::new(
            self.agent
                .get(&format!(
                    "{PLANET_REPLICATION_BASE}/changesets/{}",
                    number.changesets_path()
                ))
                .call()?
                .into_body()
                .into_reader(),
        )))?;
        Ok(changes.changesets.into_iter().map(From::from).collect())
    }
}

impl Default for ReplicationApiClient {
    fn default() -> Self {
        let agent = Config::builder()
            .user_agent(format!("Feel the streets v{}", env!("CARGO_PKG_VERSION")))
            .build()
            .new_agent();
        Self { agent }
    }
}
