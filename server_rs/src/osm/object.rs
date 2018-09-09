use std::collections::HashMap;
#[derive(Serialize, Deserialize, Clone)]
pub enum OSMObjectType {
    #[serde(rename = "node")]
    Node,
    #[serde(rename = "way")]
    Way,
    #[serde(rename = "relation")]
    Relation,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct OSMRelationMember {
    #[serde(rename = "type")]
    referenced_type: OSMObjectType,
    #[serde(rename = "ref")]
    reference: u64,
    role: String,
}

#[derive(Serialize, Deserialize, Clone)]
#[serde(tag = "type")]
pub enum OSMObjectSpecifics {
    #[serde(rename = "node")]
    Node { lat: f64, lon: f64 },
    #[serde(rename = "way")]
    Way { nodes: Vec<u64> },
    #[serde(rename = "relation")]
    Relation { members: Vec<OSMRelationMember> },
}

#[derive(Deserialize, Serialize, Clone)]
pub struct OSMObject {
    pub id: u64,
    pub timestamp: String,
    pub version: u32,
    pub changeset: u64,
    pub user: String,
    pub uid: u32,
    #[serde(default)]
    pub tags: HashMap<String, String>,
    #[serde(flatten)]
    pub specifics: OSMObjectSpecifics
}

impl OSMObject {
    
    pub fn object_type(&self) -> OSMObjectType {
        use self::OSMObjectSpecifics::*;
        match self {
            OSMObject{specifics: Node{..}, ..} => OSMObjectType::Node,
            OSMObject{specifics: Way{..}, ..} => OSMObjectType::Way,
            OSMObject{specifics: Relation{..}, ..} => OSMObjectType::Relation
        }
    }

    pub fn unique_id(&self) -> String {
                match self.object_type() {
            OSMObjectType::Node => format!("n{}", self.id),
            OSMObjectType::Way => format!("w{}", self.id),
            OSMObjectType::Relation => format!("r{}", self.id),
        }
    }
}

impl OSMRelationMember {
    pub fn unique_reference(&self) -> String {
        match self.referenced_type {
            OSMObjectType::Node => format!("n{}", self.reference),
            OSMObjectType::Way => format!("w{}", self.reference),
            OSMObjectType::Relation => format!("r{}", self.reference),
        }
    }
}
