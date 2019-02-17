use crate::object::OSMObject;

pub enum OSMObjectChangeType {
    Create,
    Modify,
    Delete,
}

pub struct OSMObjectChange {
    pub change_type: OSMObjectChangeType,
    pub old: Option<OSMObject>,
    pub new: Option<OSMObject>,
}
