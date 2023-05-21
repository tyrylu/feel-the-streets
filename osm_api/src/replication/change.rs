use crate::{Result, SmolStr};
use serde::Deserialize;
use std::convert::TryFrom;
use crate::object::OSMObject;
use crate::raw_object::OSMObject as RawOSMObject;

#[derive(Debug, Deserialize)]
pub(crate) struct ObjectsHolder {
    #[serde(rename = "$value")]
    objects: Vec<RawOSMObject>
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum RawOSMChangesPart {
    Modify(ObjectsHolder),
    Create(ObjectsHolder),
    Delete(ObjectsHolder)
}

#[derive(Debug, Deserialize)]
pub(crate) struct RawOSMChanges {
#[serde(rename = "$value")]
changes: Vec<RawOSMChangesPart>
}

#[derive(Debug)]
pub enum OSMChange {
    Modify(OSMObject),
    Create(OSMObject),
    Delete(OSMObject),
}

pub struct OSMChanges(pub Vec<OSMChange>);

impl TryFrom<RawOSMChanges> for OSMChanges {
    type Error = crate::Error;

    fn try_from(val: RawOSMChanges) -> Result<OSMChanges> {
        let mut res = vec![];
        for part in val.changes {
            use RawOSMChangesPart::*;
            match part {
                Modify(holder) => {
                    for o in holder.objects {
                        res.push(OSMChange::Modify(o.try_into()?));
                    }
                },
                Create(holder) => {
                    for o in holder.objects {
                        res.push(OSMChange::Create(o.try_into()?));
                    }
                },
                Delete(holder) => {
                    for o in holder.objects {
                        res.push(OSMChange::Delete(o.try_into()?));
                    }
                },
            }
        }
        Ok(OSMChanges(res))
    }
}

impl OSMChange {
    pub fn changeset(&self) -> u64 {
        match self {
            OSMChange::Modify(o)
            | OSMChange::Create(o)
            | OSMChange::Delete(o) => o.changeset,
        }
    }

    pub fn object_unique_id(&self) -> SmolStr {
        match self {
            OSMChange::Modify(o)
            | OSMChange::Create(o)
            | OSMChange::Delete(o) => o.unique_id(),
        }
    }
}