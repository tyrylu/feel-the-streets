use crate::Result;
use serde::Deserialize;
use std::convert::TryFrom;

use crate::object::OSMObject;
use crate::raw_object::OSMObject as RawOSMObject;

#[derive(Debug, Deserialize)]
pub(crate) struct RawOSMChange {
    #[serde(default)]
    pub modify: Vec<Modification>,
    #[serde(default)]
    pub create: Vec<Creation>,
    #[serde(default)]
    pub delete: Vec<Deletion>
}

#[derive(Debug, Deserialize)]
pub struct Modification {
    #[serde(rename = "node", alias = "way", alias = "relation")]
    changes: Vec<RawOSMObject>
}

#[derive(Debug, Deserialize)]
pub struct Creation {
    #[serde(rename = "node", alias = "way", alias = "relation")]
    changes: Vec<RawOSMObject>
}

#[derive(Debug, Deserialize)]
pub struct Deletion {
    #[serde(rename = "node", alias = "way", alias = "relation")]
    changes: Vec<RawOSMObject>
}


#[derive(Debug)]
pub struct OSMChange {
    pub modify: Vec<OSMObject>,
    pub create: Vec<OSMObject>,
    pub delete: Vec<OSMObject>,
}

impl TryFrom<RawOSMChange> for OSMChange {
    type Error = crate::Error;

    fn try_from(value: RawOSMChange) -> Result<Self> {
        let modify = value.modify.into_iter().flat_map(|c| c.changes.into_iter()).map(|o| o.try_into()).collect::<Result<Vec<OSMObject>>>()?;
        let create = value.create.into_iter().flat_map(|c| c.changes.into_iter()).map(|o| o.try_into()).collect::<Result<Vec<OSMObject>>>()?;
        let delete = value.delete.into_iter().flat_map(|c| c.changes.into_iter()).map(|o| o.try_into()).collect::<Result<Vec<OSMObject>>>()?;

        Ok(OSMChange {
            modify, create, delete
        })
    }
}
