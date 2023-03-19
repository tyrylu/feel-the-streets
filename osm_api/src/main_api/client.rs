use crate::Result;
use super::changeset::Changeset;
use super::raw_changeset::RawChangesets;
use quick_xml::de;
use std::io::BufReader;
use ureq::Agent;

const MAIN_API_BASE: &str = "https://openstreetmap.org/api/0.6";

pub struct MainAPIClient {
    agent: Agent
}

impl MainAPIClient {
    pub fn get_changeset(&self, changeset: u64) -> Result<Changeset> {
        let mut changesets: RawChangesets = de::from_reader(BufReader::new(self.agent.get(&format!("{MAIN_API_BASE}/changeset/{changeset}")).call()?.into_reader()))?;
        Ok(changesets.changesets.pop().unwrap().into())
    }
}

impl Default for MainAPIClient {
    fn default() -> Self {
        Self { agent: Agent::new() }
    }
}