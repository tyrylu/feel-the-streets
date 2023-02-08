mod api;
mod change;
pub use api::ReplicationApiClient;
pub use change::OSMChange;

use std::str::FromStr;

pub struct SequenceNumber(pub u32);

pub struct ReplicationState {
    pub sequence_number: SequenceNumber,
    pub timestamp: String
}

impl FromStr for ReplicationState {
    type Err = Error;
    fn from_str(val: &str) -> Result<Self, Self::Err> {
        let mut sn = None;
        let mut ts = None;
        for line in val.lines() {
            if line.starts_with('#') {
                continue;
            }
            let parts: Vec<_> = line.split('=').collect();
            match parts[0] {
                "sequenceNumber" => sn = Some(SequenceNumber::from_str(parts[1])?),
                "timestamp" => ts = Some(parts[1]),
                key => return Err(Error::UnknownKey(key.to_string()))
            }
        }
        match (sn, ts) {
            (Some(s), Some(t)) => Ok(Self { sequence_number: s, timestamp: t.to_string()}),
            (Some(_), None) => Err(Error::MissingTimestamp),
            (None, Some(_)) => Err(Error::MissingSequenceNumber),
            (None, None) => Err(Error::NoData)
        }
    }
}

#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("Missing sequence number in replication state")]
    MissingSequenceNumber,
    #[error("Sequence number is out of range")]
    SequenceNumberOutOfRange,
    #[error("Sequence number is not numeric")]
    SequenceNumberNotNumeric,
    #[error("Missing timestamp in replication state")]
    MissingTimestamp,
    #[error("No data in replication state")]
    NoData,
    #[error("Unknown replication state key: {0}")]
    UnknownKey(String)
}

impl FromStr for SequenceNumber {
    type Err = Error;
    fn from_str(val: &str) -> Result<Self, Self::Err> {
        match val.parse() {
            Ok(n) => Self::from_u32(n),
            Err(_) => Err(Error::SequenceNumberNotNumeric)
        }
    }
}

impl SequenceNumber {
    
    pub fn from_u32(num: u32) -> Result<Self, Error> {
        if num > 999_999_999 {
            Err(Error::SequenceNumberOutOfRange)
        }
        else {
            Ok(Self(num))
        }
    }

    pub fn as_uri_path(&self) -> String {
        let padded = format!("{:0>9}", self.0);
        format!("{}/{}/{}.osc.gz", &padded[0..=2], &padded[3..=5], &padded[6..=8])
    }
}

