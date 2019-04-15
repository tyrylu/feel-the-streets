use crate::change::{OSMObjectChange, OSMObjectChangeType};
use crate::object::*;
use crate::Result;
use std::collections::HashMap;
use std::io::Read;
use xml::{attribute::OwnedAttribute, reader::XmlEvent, EventReader};

fn convert_to_map(attributes: Vec<OwnedAttribute>) -> HashMap<String, String> {
    let mut map = HashMap::new();
    for attr in attributes {
        map.insert(attr.name.local_name, attr.value);
    }
    map
}

pub struct OSMObjectChangeIterator<T: Read> {
    reader: EventReader<T>,
    finished: bool,
    current_change: Option<OSMObjectChange>,
    current_change_type: Option<OSMObjectChangeType>,
    old: Option<OSMObject>,
    new: Option<OSMObject>,
}

impl<T: Read> OSMObjectChangeIterator<T> {
    pub fn new(readable: T) -> Self {
        OSMObjectChangeIterator {
            reader: EventReader::new(readable),
            finished: false,
            current_change: None,
            current_change_type: None,
            old: None,
            new: None,
        }
    }

    fn parse_object(&mut self) -> Result<OSMObject> {
        trace!("Parse object.");
        let mut tags: HashMap<String, String> = HashMap::new();
        let mut members = Vec::new();
        let mut nodes = Vec::new();
        // The rust compiler needs some initial values for the variables. They'll be replaced during the parsing, but i did not see a way (excluding using Options) how to convince the rust compiler about that.
        let (
            mut id,
            mut timestamp,
            mut version,
            mut changeset,
            mut user,
            mut uid,
            mut lon,
            mut lat,
        ) = (
            0,
            "".to_string(),
            0,
            0,
            "".to_string(),
            0,
            0 as f64,
            0 as f64,
        );
        loop {
            let event = self.reader.next();
            let event = event?;
            match event {
                XmlEvent::Whitespace(..) => {}
                XmlEvent::StartElement {
                    name, attributes, ..
                } => {
                    let mut attrs = convert_to_map(attributes);
                    match name.local_name.as_ref() {
                        "node" | "way" | "relation" => {
                            id = attrs["id"].parse().expect("Could not parse id as an u64.");
                            version = attrs["version"]
                                .parse()
                                .expect("Could not parse version as an u32.");
                            timestamp = attrs.remove("timestamp").expect("No timestamp in attrs.");
                            changeset = attrs["changeset"]
                                .parse()
                                .expect("Could not parse changeset as an u64.");
                            uid = attrs["uid"]
                                .parse()
                                .expect("Could not parse uid as an u32.");
                            user = attrs.remove("user").expect("No user in attrs.");
                            if attrs.contains_key("lon") {
                                lon = attrs["lon"].parse().expect("Could not parse lon as a f64.");
                                lat = attrs["lat"].parse().expect("Could not parse lat as a f64.");
                            }
                        }
                        "tag" => {
                            tags.insert(
                                attrs.remove("k").expect("No k in attrs"),
                                attrs.remove("v").expect("No v in attrs."),
                            );
                        }
                        "nd" => nodes.push(
                            attrs["ref"]
                                .parse()
                                .expect("Could not parse node ref as an u64."),
                        ),
                        "member" => members.push(OSMRelationMember::new(
                            attrs["ref"]
                                .parse()
                                .expect("Could not parse member ref as an u64."),
                            OSMObjectType::from_str(&attrs["type"])
                                .expect("Could not parse referenced object type."),
                            attrs.remove("role").expect("No role in attrs."),
                        )),
                        _ => panic!("Unexpected start of element {}.", name.local_name),
                    }
                }
                XmlEvent::EndElement { name, .. } => match name.local_name.as_ref() {
                    "node" => {
                        return Ok(OSMObject::new_node(
                            id, timestamp, version, changeset, user, uid, tags, lat, lon,
                        ));
                    }
                    "way" => {
                        return Ok(OSMObject::new_way(
                            id, timestamp, version, changeset, user, uid, tags, nodes,
                        ));
                    }
                    "relation" => {
                        return Ok(OSMObject::new_rel(
                            id, timestamp, version, changeset, user, uid, tags, members,
                        ));
                    }
                    "tag" | "nd" | "member" => {}
                    _ => panic!("Unexpected end of element {}.", name.local_name),
                },
                _ => panic!("Unexpected event during xml parsing."),
            }
        }
    }

    fn parse_change_step(&mut self) -> Result<()> {
        trace!("Doing a parse change step.");
        let mut in_remark = false;
        match self.reader.next() {
            Ok(XmlEvent::StartDocument { .. }) => trace!("Start document."),
            Ok(XmlEvent::Whitespace(..)) => trace!("whitespace."),
            Ok(XmlEvent::Characters(chars)) => {
                trace!("Characters: {}", chars);
                if in_remark {
                    warn!("Received a remark from the server: {}", chars);
                }
            }
            Ok(XmlEvent::EndDocument) => {
                trace!("End document.");
                self.finished = true;
            }
            Ok(XmlEvent::StartElement {
                name, attributes, ..
            }) => match name.local_name.as_ref() {
                "action" => {
                    self.current_change = None;
                    let attrs = convert_to_map(attributes);
                    self.old = None;
                    self.new = None;
                    self.current_change_type = match attrs["type"].as_ref() {
                        "create" => Some(OSMObjectChangeType::Create),
                        "modify" => Some(OSMObjectChangeType::Modify),
                        "delete" => Some(OSMObjectChangeType::Delete),
                        _ => panic!("Unknown change type {}.", attrs["type"]),
                    };
                    if let Some(OSMObjectChangeType::Create) = self.current_change_type {
                        self.new = Some(self.parse_object()?);
                    }
                }
                "new" => self.new = Some(self.parse_object()?),
                "old" => self.old = Some(self.parse_object()?),
                "remark" => in_remark = true,
                "osm" | "note" | "meta" => {}
                _ => panic!("Start of unexpected tag {}.", name.local_name),
            },
            Ok(XmlEvent::EndElement { name, .. }) => match name.local_name.as_ref() {
                "action" => {
                    self.current_change = Some(OSMObjectChange {
                        change_type: self
                            .current_change_type
                            .take()
                            .expect("Did not set change type?"),
                        old: self.old.take(),
                        new: self.new.take(),
                    })
                }
                "osm3response" => self.finished = true,
                "remark" => in_remark = false,
                "note" | "osm" | "meta" | "old" | "new" => {}
                _ => panic!("Unexpected end of {}.", name.local_name),
            },
            Err(e) => {
                self.finished = true;
                return Err(failure::Error::from(e));
            }
            event @ _ => panic!(format!("Unexpected event during parsing: {:?}", event)),
        }
        Ok(())
    }
}

impl<T: Read> Iterator for OSMObjectChangeIterator<T> {
    type Item = Result<OSMObjectChange>;

    fn next(&mut self) -> Option<Self::Item> {
        trace!("Next change requested.");
        loop {
            match self.parse_change_step() {
                Err(e) => return Some(Err(e)),
                Ok(()) => {
                    if self.finished {
                        trace!("Finished.");
                        return None;
                    }
                    if self.current_change.is_some() {
                        return Some(Ok(self.current_change.take()?));
                    }
                }
            }
        }
    }
}
