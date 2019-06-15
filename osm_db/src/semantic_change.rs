use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Serialize, Deserialize, Debug)]
pub enum EntryChange {
    Create { key: String, value: Value },
    Update { key: String, new_value: Value },
    Remove { key: String },
}

impl EntryChange {
    pub fn updating(key: &str, new_value: Value) -> Self {
        EntryChange::Update {
            key: key.to_string(),
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

#[derive(Serialize, Deserialize, Debug)]
pub enum SemanticChange {
    Create {
        geometry: String,
        discriminator: String,
        data: String,
        effective_width: Option<f64>,
    },
    Remove {
        osm_id: String,
    },
    Update {
        osm_id: String,
        property_changes: Vec<EntryChange>,
        data_changes: Vec<EntryChange>,
    },
}

impl SemanticChange {
    pub fn creating(
        geometry: String,
        discriminator: String,
        data: String,
        effective_width: Option<f64>,
    ) -> Self {
        SemanticChange::Create {
            geometry,
            discriminator,
            data,
            effective_width,
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
    ) -> Self {
        SemanticChange::Update {
            property_changes,
            data_changes,
            osm_id: osm_id.to_string(),
        }
    }
}
