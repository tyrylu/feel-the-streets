use crate::Error;
use serde::Deserialize;
use smol_str::SmolStr;

#[derive(Debug, Deserialize)]
pub(crate) struct Tag {
    #[serde(rename = "@k")]
    pub(crate) k: SmolStr,
    #[serde(rename = "@v")]
    pub(crate) v: SmolStr,
}

#[derive(Debug, Deserialize)]
pub(crate) struct OSMNode {
    #[serde(rename = "@id")]
    pub id: u64,
    #[serde(rename = "@timestamp")]
    pub timestamp: SmolStr,
    #[serde(rename = "@version")]
    pub version: u32,
    #[serde(rename = "@changeset")]
    pub changeset: u64,
    #[serde(rename = "@user")]
    pub user: SmolStr,
    #[serde(rename = "@uid")]
    pub uid: u32,
    #[serde(rename = "@lat")]
    pub lat: f64,
    #[serde(rename = "@lon")]
    pub lon: f64,
    #[serde(default, rename = "tag")]
    pub tags: Vec<Tag>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct NodeRef {
    #[serde(rename = "@ref")]
    pub(crate) reference: u64,
}

#[derive(Debug, Deserialize)]
pub(crate) struct OSMWay {
    #[serde(rename = "@id")]
    pub id: u64,
    #[serde(rename = "@timestamp")]
    pub timestamp: SmolStr,
    #[serde(rename = "@version")]
    pub version: u32,
    #[serde(rename = "@changeset")]
    pub changeset: u64,
    #[serde(rename = "@user")]
    pub user: SmolStr,
    #[serde(rename = "@uid")]
    pub uid: u32,
    #[serde(default, rename = "nd")]
    pub nodes: Vec<NodeRef>,
    #[serde(default, rename = "tag")]
    pub tags: Vec<Tag>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct RelationMember {
    #[serde(rename = "@type")]
    pub(crate) referenced_type: SmolStr,
    #[serde(rename = "@ref")]
    pub(crate) reference: u64,
    #[serde(rename = "@role")]
    pub(crate) role: SmolStr,
}

#[derive(Debug, Deserialize)]
pub(crate) struct OSMRelation {
    #[serde(rename = "@id")]
    pub id: u64,
    #[serde(rename = "@timestamp")]
    pub timestamp: SmolStr,
    #[serde(rename = "@version")]
    pub version: u32,
    #[serde(rename = "@changeset")]
    pub changeset: u64,
    #[serde(rename = "@user")]
    pub user: SmolStr,
    #[serde(rename = "@uid")]
    pub uid: u32,
    #[serde(rename = "member", default)]
    pub members: Vec<RelationMember>,
    #[serde(default, rename = "tag")]
    pub tags: Vec<Tag>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum OSMObject {
    Node(OSMNode),
    Way(OSMWay),
    Relation(OSMRelation),
}

#[derive(Deserialize)]
pub(crate) struct RemarkElement {
    #[serde(rename = "$text")]
    remark: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum OSMObjectOrRemark {
    Node(OSMNode),
    Way(OSMWay),
    Relation(OSMRelation),
    Remark(RemarkElement),
}

impl TryInto<OSMObject> for OSMObjectOrRemark {
    type Error = Error;

    fn try_into(self) -> Result<OSMObject, Self::Error> {
        use OSMObjectOrRemark::*;
        match self {
            Node(n) => Ok(OSMObject::Node(n)),
            Way(w) => Ok(OSMObject::Way(w)),
            Relation(r) => Ok(OSMObject::Relation(r)),
            Remark(elem) => Err(Error::OverpassAPIError(elem.remark)),
        }
    }
}
