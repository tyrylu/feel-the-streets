use super::changeset::Changeset;
use super::raw_changeset::RawChangesets;
use crate::Result;
use backon::{BlockingRetryable, ExponentialBuilder};
use log::warn;
use quick_xml::de;
use std::io::BufReader;
use ureq::Agent;

const MAIN_API_BASE: &str = "https://www.openstreetmap.org/api/0.6";

pub struct MainAPIClient {
    agent: Agent,
}

impl MainAPIClient {
    pub fn get_changeset(&self, changeset: u64) -> Result<Changeset> {
        let get_reader = || {
            self.agent
                .get(&format!("{MAIN_API_BASE}/changeset/{changeset}"))
                .call()
        };
        let reader = get_reader
            .retry(&ExponentialBuilder::default())
            .notify(|e, dur| {
                warn!(
                    "Could not get changeset {}, error: {:?}, going to sleep for {:?}.",
                    changeset, e, dur
                );
            })
            .call()?
            .into_reader();
        let mut changesets: RawChangesets = de::from_reader(BufReader::new(reader))?;

        Ok(changesets.changesets.pop().unwrap().into())
    }
}

impl Default for MainAPIClient {
    fn default() -> Self {
        Self {
            agent: Agent::new(),
        }
    }
}
