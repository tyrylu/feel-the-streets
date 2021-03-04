use crate::Error;
use hashbrown::HashMap;
use std::iter;
use std::str::FromStr;
use smol_str::SmolStr;

#[derive(Serialize, Deserialize, Clone, PartialEq, Debug)]
pub enum OSMObjectType {
    #[serde(rename = "node")]
    Node,
    #[serde(rename = "way")]
    Way,
    #[serde(rename = "relation")]
    Relation,
}

impl FromStr for OSMObjectType {
    type Err = Error;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        match value {
            "node" => Ok(OSMObjectType::Node),
            "way" => Ok(OSMObjectType::Way),
            "relation" => Ok(OSMObjectType::Relation),
            node_type => Err(Error::UnknownNodeType(node_type.to_string())),
        }
    }
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct OSMRelationMember {
    #[serde(rename = "type")]
    referenced_type: OSMObjectType,
    #[serde(rename = "ref")]
    reference: u64,
    pub role: String,
}

impl OSMRelationMember {
    pub fn new(reference: u64, referenced_type: OSMObjectType, role: String) -> Self {
        OSMRelationMember {
            reference,
            referenced_type,
            role,
        }
    }
}

#[derive(Serialize, Deserialize, Clone, Debug)]
#[serde(tag = "type")]
pub enum OSMObjectSpecificsFromNetwork {
    #[serde(rename = "node")]
    Node { lat: f64, lon: f64 },
    #[serde(rename = "way")]
    Way { nodes: Vec<u64> },
    #[serde(rename = "relation")]
    Relation { members: Vec<OSMRelationMember> },
}

impl OSMObjectSpecificsFromNetwork {
    fn into_internal(self) -> OSMObjectSpecifics {
        use OSMObjectSpecificsFromNetwork::*;
        match self {
            Node { lat, lon } => OSMObjectSpecifics::Node { lat, lon },
            Way { nodes } => OSMObjectSpecifics::Way { nodes },
            Relation { members } => OSMObjectSpecifics::Relation { members },
        }
    }
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub enum OSMObjectSpecifics {
    #[serde(rename = "node")]
    Node { lat: f64, lon: f64 },
    #[serde(rename = "way")]
    Way { nodes: Vec<u64> },
    #[serde(rename = "relation")]
    Relation { members: Vec<OSMRelationMember> },
}

#[derive(Deserialize, Serialize, Clone, Debug)]
pub struct OSMObjectFromNetwork {
    pub id: u64,
    pub timestamp: String,
    pub version: u32,
    pub changeset: u64,
    pub user: String,
    pub uid: u32,
    #[serde(default)]
    pub tags: HashMap<String, String>,
    #[serde(flatten)]
    pub specifics: OSMObjectSpecificsFromNetwork,
}

#[derive(Deserialize, Serialize, Clone, Debug)]
pub struct OSMObject {
    pub id: u64,
    pub timestamp: String,
    pub version: u32,
    pub changeset: u64,
    pub user: String,
    pub uid: u32,
    #[serde(default)]
    pub tags: HashMap<String, String>,
    pub specifics: OSMObjectSpecifics,
}

impl OSMObjectFromNetwork {
    pub fn into_osm_object(self) -> OSMObject {
        OSMObject {
            id: self.id,
            timestamp: self.timestamp,
            version: self.version,
            changeset: self.changeset,
            uid: self.uid,
            user: self.user,
            tags: self.tags,
            specifics: self.specifics.into_internal(),
        }
    }
}

impl OSMObject {
    pub fn new_node(
        id: u64,
        timestamp: String,
        version: u32,
        changeset: u64,
        user: String,
        uid: u32,
        tags: HashMap<String, String>,
        lat: f64,
        lon: f64,
    ) -> OSMObject {
        OSMObject {
            id,
            timestamp,
            version,
            changeset,
            user,
            uid,
            tags,
            specifics: OSMObjectSpecifics::Node { lat, lon },
        }
    }

    pub fn new_way(
        id: u64,
        timestamp: String,
        version: u32,
        changeset: u64,
        user: String,
        uid: u32,
        tags: HashMap<String, String>,
        nodes: Vec<u64>,
    ) -> OSMObject {
        OSMObject {
            id,
            timestamp,
            version,
            changeset,
            user,
            uid,
            tags,
            specifics: OSMObjectSpecifics::Way { nodes },
        }
    }

    pub fn new_rel(
        id: u64,
        timestamp: String,
        version: u32,
        changeset: u64,
        user: String,
        uid: u32,
        tags: HashMap<String, String>,
        members: Vec<OSMRelationMember>,
    ) -> OSMObject {
        OSMObject {
            id,
            timestamp,
            version,
            changeset,
            user,
            uid,
            tags,
            specifics: OSMObjectSpecifics::Relation { members },
        }
    }

    pub fn object_type(&self) -> OSMObjectType {
        use self::OSMObjectSpecifics::*;
        match self {
            OSMObject {
                specifics: Node { .. },
                ..
            } => OSMObjectType::Node,
            OSMObject {
                specifics: Way { .. },
                ..
            } => OSMObjectType::Way,
            OSMObject {
                specifics: Relation { .. },
                ..
            } => OSMObjectType::Relation,
        }
    }

    pub fn unique_id(&self) -> SmolStr {
        match self.object_type() {
            OSMObjectType::Node => SmolStr::new_inline(&format!("n{}", self.id)),
            OSMObjectType::Way => SmolStr::new_inline(&format!("w{}", self.id)),
            OSMObjectType::Relation => SmolStr::new_inline(&format!("r{}", self.id)),
        }
    }

    pub fn related_ids(&self) -> Box<dyn Iterator<Item = (String, Option<String>)>> {
        use OSMObjectSpecifics::*;
        match self.specifics {
            Node { .. } => Box::new(iter::empty()),
            Way { ref nodes, .. } => {
                Box::new(nodes.clone().into_iter().map(|n| (format!("n{}", n), None)))
            }
            Relation { ref members, .. } => Box::new(
                members
                    .clone()
                    .into_iter()
                    .map(|m| (m.unique_reference(), Some(m.role))),
            ),
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

impl AsRef<OSMObject> for OSMObject {
    fn as_ref(&self) -> &OSMObject {
        &self
    }
}
