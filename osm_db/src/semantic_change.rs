use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum EntryChange {
    Create {
        key: String,
        value: Value,
    },
    Update {
        key: String,
        old_value: Value,
        new_value: Value,
    },
    Remove {
        key: String,
    },
}

impl EntryChange {
    pub fn updating(key: &str, old_value: Value, new_value: Value) -> Self {
        EntryChange::Update {
            key: key.to_string(),
            old_value,
            new_value,
        }
    }
    pub fn creating(key: &str, value: Value) -> Self {
        EntryChange::Create {
            key: key.to_string(),
            value,
        }
    }
    pub fn removing(key: &str) -> Self {
        EntryChange::Remove {
            key: key.to_string(),
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum ListChange {
    Add { value: String },
    Remove { value: String },
}

impl ListChange {
    pub fn adding(value: String) -> Self {
        ListChange::Add { value }
    }

    pub fn removing(value: String) -> Self {
        ListChange::Remove { value }
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum SemanticChange {
    RedownloadDatabase,
    Create {
        id: String,
        geometry: String,
        discriminator: String,
        data: String,
        effective_width: Option<f64>,
        child_ids: Vec<String>,
    },
    Remove {
        osm_id: String,
    },
    Update {
        osm_id: String,
        property_changes: Vec<EntryChange>,
        data_changes: Vec<EntryChange>,
        child_id_changes: Vec<ListChange>,
    },
}

impl SemanticChange {
    pub fn creating(
        id: String,
        geometry: Vec<u8>,
        discriminator: String,
        data: String,
        effective_width: Option<f64>,
        child_ids: Vec<String>,
    ) -> Self {
        SemanticChange::Create {
            geometry: base64::encode(&geometry),
            id,
            discriminator,
            data,
            effective_width,
            child_ids,
        }
    }
    pub fn removing(osm_id: &str) -> Self {
        SemanticChange::Remove {
            osm_id: osm_id.to_string(),
        }
    }

    pub fn updating(
        osm_id: &str,
        property_changes: Vec<EntryChange>,
        data_changes: Vec<EntryChange>,
        child_id_changes: Vec<ListChange>,
    ) -> Self {
        SemanticChange::Update {
            property_changes,
            data_changes,
            child_id_changes,
            osm_id: osm_id.to_string(),
        }
    }
}
