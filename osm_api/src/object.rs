#![allow(clippy::too_many_arguments)]
use crate::raw_object::{OSMObject as RawOSMObject, RelationMember, Tag};
use crate::{Error, Result};
use hashbrown::HashMap;
use serde::{Deserialize, Serialize};
use smol_str::{format_smolstr, SmolStr};
use std::convert::TryFrom;
use std::iter;
use std::str::FromStr;

#[derive(Serialize, Deserialize, Clone, PartialEq, Eq, Debug)]
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

    fn from_str(value: &str) -> Result<Self> {
        match value {
            "node" => Ok(OSMObjectType::Node),
            "way" => Ok(OSMObjectType::Way),
            "relation" => Ok(OSMObjectType::Relation),
            node_type => Err(Error::UnknownNodeType(node_type.to_string())),
        }
    }
}

impl OSMObjectType {
    pub fn create_string_id(&self, id: u64) -> SmolStr {
        use OSMObjectType::*;
        match self {
            Node => format_smolstr!("n{}", id),
            Way => format_smolstr!("w{}", id),
            Relation => format_smolstr!("r{}", id),
        }
    }
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct OSMRelationMember {
    #[serde(rename = "type")]
    referenced_type: OSMObjectType,
    #[serde(rename = "ref")]
    reference: u64,
    pub role: SmolStr,
}

impl OSMRelationMember {
    pub fn new(reference: u64, referenced_type: OSMObjectType, role: String) -> Self {
        OSMRelationMember {
            referenced_type,
            reference,
            role: role.into(),
        }
    }
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub enum OSMObjectSpecifics {
    #[serde(rename = "node")]
    Node { lat: f64, lon: f64 },
    #[serde(rename = "way")]
    Way { nodes: Vec<u64> },
    #[serde(rename = "relation")]
    Relation { members: Vec<OSMRelationMember> },
}

#[derive(Deserialize, Serialize, Clone, Debug, PartialEq)]
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
        self.object_type().create_string_id(self.id)
    }

    pub fn related_ids(&self) -> Box<dyn Iterator<Item = (SmolStr, Option<SmolStr>)>> {
        use OSMObjectSpecifics::*;
        match self.specifics {
            Node { .. } => Box::new(iter::empty()),
            Way { ref nodes, .. } => Box::new(
                nodes
                    .clone()
                    .into_iter()
                    .map(|n| (format_smolstr!("n{n}"), None)),
            ),
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
    pub fn unique_reference(&self) -> SmolStr {
        self.referenced_type.create_string_id(self.reference)
    }
}

impl AsRef<OSMObject> for OSMObject {
    fn as_ref(&self) -> &OSMObject {
        self
    }
}

impl TryFrom<RawOSMObject> for OSMObject {
    type Error = Error;

    fn try_from(raw_object: RawOSMObject) -> Result<Self> {
        match raw_object {
            RawOSMObject::Node(n) => Ok(OSMObject::new_node(
                n.id,
                n.timestamp.into(),
                n.version,
                n.changeset,
                n.user.into(),
                n.uid,
                to_tags_hashmap(n.tags),
                n.lat,
                n.lon,
            )),
            RawOSMObject::Way(w) => Ok(OSMObject::new_way(
                w.id,
                w.timestamp.into(),
                w.version,
                w.changeset,
                w.user.into(),
                w.uid,
                to_tags_hashmap(w.tags),
                w.nodes.iter().map(|n| n.reference).collect(),
            )),
            RawOSMObject::Relation(r) => Ok(OSMObject::new_rel(
                r.id,
                r.timestamp.into(),
                r.version,
                r.changeset,
                r.user.into(),
                r.uid,
                to_tags_hashmap(r.tags),
                to_typed_members(r.members)?,
            )),
        }
    }
}

fn to_tags_hashmap(tags: Vec<Tag>) -> HashMap<String, String> {
    let mut ret = HashMap::with_capacity(tags.len());
    for tag in tags {
        ret.insert(tag.k.into(), tag.v.into());
    }
    ret
}

fn to_typed_members(members: Vec<RelationMember>) -> Result<Vec<OSMRelationMember>> {
    let mut ret = Vec::with_capacity(members.len());
    for member in members {
        ret.push(OSMRelationMember::new(
            member.reference,
            OSMObjectType::from_str(member.referenced_type.as_str())?,
            member.role.into(),
        ));
    }
    Ok(ret)
}
