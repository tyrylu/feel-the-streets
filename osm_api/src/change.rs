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
