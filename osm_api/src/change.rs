use crate::object::OSMObject;

#[derive(Debug)]
pub enum OSMObjectChangeType {
    Create,
    Modify,
    Delete,
}

#[derive(Debug)]
pub struct OSMObjectChange {
    pub change_type: OSMObjectChangeType,
    pub old: Option<OSMObject>,
    pub new: Option<OSMObject>,
}

/// We are most often anyway constructing the Change wariant, so it would be a needless indirection most of the time.
#[allow(clippy::large_enum_variant)]
pub enum OSMObjectChangeEvent {
    Change(OSMObjectChange),
    Remark(String)
}