use crate::Result;
use std::fs;

const LATEST_SN_FILE: &str = "latest_processed.sn";

pub(crate) fn read_latest_sequence_number() -> Result<u32> {
    let content = fs::read_to_string(LATEST_SN_FILE)?;
    Ok(content.parse().expect("Could not parse latest sequence number"))
}

pub(crate) fn save_latest_sequence_number(number: u32) -> Result<()> {
    Ok(fs::write(LATEST_SN_FILE, number.to_string())?)
}