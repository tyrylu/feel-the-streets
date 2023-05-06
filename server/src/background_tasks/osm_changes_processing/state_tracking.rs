use crate::Result;
use log::info;
use std::fs;
use std::path::Path;

const LATEST_SN_FILE: &str = "latest_processed.sn";

pub(crate) fn read_latest_sequence_number() -> Result<u32> {
    if Path::new(LATEST_SN_FILE).exists() {
        let content = fs::read_to_string(LATEST_SN_FILE)?;
        Ok(content
            .parse()
            .expect("Could not parse latest sequence number"))
    } else {
        info!("Latest processed sequence number not stored, using default.");
        Ok(5_400_000)
    }
}

pub(crate) fn save_latest_sequence_number(number: u32) -> Result<()> {
    Ok(fs::write(LATEST_SN_FILE, number.to_string())?)
}
