use osm_api::replication::{ReplicationApiClient, SequenceNumber};
use osm_api::Result;
use std::env;
fn main() -> Result<()> {
    // Collect command line arguments
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <batch_number>", args[0]);
        eprintln!("Example: {} 6000000", args[0]);
        std::process::exit(1);
    }
    // Parse the batch number from the command line
    let batch_number: u32 = args[1].parse().expect("Batch number must be a
      valid integer");
    // Initialize the replication client
    // By default, it uses the official OSM planet replication base URL
    let client = ReplicationApiClient::default();

    println!("Fetching changes from batch {}...", batch_number);

    // Retrieve the changesets for the given sequence number
    let changes = client.get_change(SequenceNumber(batch_number))?;
    println!("Found {} changes in batch {}.\n", changes.0.len(),
    batch_number);
    Ok(())
}
