use crate::Result;
use serde::Deserialize;
use std::convert::TryFrom;

use crate::object::OSMObject;
use crate::raw_object::OSMObject as RawOSMObject;

#[derive(Debug, Deserialize)]
pub(crate) struct RawOSMChange {
    pub modify: Vec<RawOSMObject>,
    pub create: Vec<RawOSMObject>,
    pub delete: Vec<RawOSMObject>,
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
        Ok(OSMChange {
            create: value
                .create
                .into_iter()
                .map(|o| o.try_into())
                .collect::<Result<Vec<OSMObject>>>()?,
            modify: value
                .modify
                .into_iter()
                .map(|o| o.try_into())
                .collect::<Result<Vec<OSMObject>>>()?,
            delete: value
                .delete
                .into_iter()
                .map(|o| o.try_into())
                .collect::<Result<Vec<OSMObject>>>()?,
        })
    }
}
