use osm_api::replication::{ReplicationApiClient, SequenceNumber};

#[test]
fn test_parse_change_6993700() {
    let client = ReplicationApiClient::default();
    let change = client.get_change(SequenceNumber(6993700)).expect("Could not get change 6993700");
    assert_eq!(change.0.len(), 29592);
}

#[test]
fn test_parse_changesets_batch_6899012() {
    let client = ReplicationApiClient::default();
    let changesets = client.get_changesets(SequenceNumber(6899012)).expect("Could not get changesets batch 6899012");
    assert_eq!(changesets.len(), 44);
}

