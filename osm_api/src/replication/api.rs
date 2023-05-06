use super::change::RawOSMChange;
use super::{OSMChange, ReplicationState, SequenceNumber};
use crate::Result;
use flate2::read::GzDecoder;
use std::io::BufReader;
use std::str::FromStr;
use ureq::Agent;

const PLANET_REPLICATION_BASE: &str = "https://planet.openstreetmap.org/replication";

pub struct ReplicationApiClient {
    agent: Agent,
}

impl ReplicationApiClient {
    pub fn latest_replication_state(&self) -> Result<ReplicationState> {
        Ok(ReplicationState::from_str(
            &self
                .agent
                .get(&format!("{PLANET_REPLICATION_BASE}/minute/state.txt"))
                .call()?
                .into_string()?,
        )?)
    }

    pub fn get_change(&self, number: SequenceNumber) -> Result<OSMChange> {
        let change: RawOSMChange = quick_xml::de::from_reader(BufReader::new(GzDecoder::new(
            self.agent
                .get(&format!(
                    "{PLANET_REPLICATION_BASE}/minute/{}",
                    number.data_path()
                ))
                .call()?
                .into_reader(),
        )))?;
        change.try_into()
    }

    pub fn get_change_stats(&self, number: &SequenceNumber) -> Result<ReplicationState> {
        Ok(ReplicationState::from_str(
            &self
                .agent
                .get(&format!(
                    "{PLANET_REPLICATION_BASE}/minute/{}",
                    number.stats_path()
                ))
                .call()?
                .into_string()?,
        )?)
    }
}

impl Default for ReplicationApiClient {
    fn default() -> Self {
        Self {
            agent: Agent::new(),
        }
    }
}
