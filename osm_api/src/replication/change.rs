use crate::{Result, SmolStr};
use serde::Deserialize;
use std::convert::TryFrom;
use crate::object::OSMObject;
use crate::raw_object::OSMObject as RawOSMObject;

#[derive(Debug, Deserialize)]
#[serde(rename_all = "snake_case")]
pub(crate) enum RawOSMChangesPart {
    Modify(Vec<RawOSMObject>),
    Create(Vec<RawOSMObject>),
    Delete(Vec<RawOSMObject>)
}

#[derive(Debug)]
pub enum OSMChange {
    Modify(OSMObject),
    Create(OSMObject),
    Delete(OSMObject),
}

pub(crate) type RawOSMChanges = Vec<RawOSMChangesPart>;
pub struct OSMChanges(pub Vec<OSMChange>);

impl TryFrom<RawOSMChanges> for OSMChanges {
    type Error = crate::Error;

    fn try_from(val: RawOSMChanges) -> Result<OSMChanges> {
        let mut res = vec![];
        for part in val {
            use RawOSMChangesPart::*;
            match part {
                Modify(objs) => {
                    for o in objs {
                        res.push(OSMChange::Modify(o.try_into()?));
                    }
                },
                Create(objs) => {
                    for o in objs {
                        res.push(OSMChange::Create(o.try_into()?));
                    }
                },
                Delete(objs) => {
                    for o in objs {
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