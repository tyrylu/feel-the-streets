use crate::Result;
use log::info;
use std::fs;
use std::path::Path;

pub(crate) fn read_latest_sequence_number(filename: &str, default: u32) -> Result<u32> {
    if Path::new(filename).exists() {
        let content = fs::read_to_string(filename)?;
        Ok(content
            .trim_end_matches('\n')
            .parse()
            .expect("Could not parse latest sequence number"))
    } else {
        info!("Latest processed sequence number not storedin {}, using the default of {}.", filename, default);
        Ok(default)
    }
}

pub(crate) fn save_latest_sequence_number(filename: &str, number: u32) -> Result<()> {
    Ok(fs::write(filename, number.to_string())?)
}
