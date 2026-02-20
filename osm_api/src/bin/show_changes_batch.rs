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

    println!("Fetching changesets from batch {}...", batch_number);

    // Retrieve the changesets for the given sequence number
    let changesets = client.get_changesets(SequenceNumber(batch_number))?;
    println!("Found {} changesets in batch {}.\n", changesets.len(),
    batch_number);

    for (i, changeset) in changesets.iter().enumerate() {
        println!("--- Changeset #{} (ID: {}) ---", i + 1, changeset.id);
        println!("  Created at:     {}", changeset.created_at);
        println!("  User:           {} (ID: {})", changeset.user,
      changeset.uid);
        println!("  State:          {:?}", changeset.state);

        if let Some(bounds) = &changeset.bounds {
            println!("  Bounds:         min_lon: {}, min_lat: {}, max_lon:
      {}, max_lat: {}",
                     bounds.min_x, bounds.min_y, bounds.max_x,
      bounds.max_y);
        }
        println!("  Changes count:  {}", changeset.changes_count);
        println!("  Comments count: {}", changeset.comments_count);
        if !changeset.tags.is_empty() {
            println!("  Tags:");
            for (k, v) in &changeset.tags {
                println!("    {}: {}", k, v);
            }
        }
        println!();
    }
    Ok(())
}
