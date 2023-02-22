use crate::change::{OSMObjectChange, OSMObjectChangeEvent, OSMObjectChangeType};
use crate::object::*;
use crate::Error;
use crate::Result;
use hashbrown::HashMap;
use log::trace;
use quick_xml::{
    events::{attributes::Attributes, Event},
    Reader,
};
use std::io::{BufReader, Read};
use std::str::FromStr;

fn convert_to_map(attributes: Attributes) -> Result<HashMap<String, String>> {
    let mut map = HashMap::new();
    for attr in attributes {
        let attr = attr?;
        map.insert(
            String::from_utf8_lossy(attr.key.local_name().as_ref()).to_string(),
            attr.unescape_value()?.to_string(),
        );
    }
    Ok(map)
}

pub struct OSMObjectChangeIterator<T: Read> {
    reader: Reader<BufReader<T>>,
    finished: bool,
    current_event: Option<OSMObjectChangeEvent>,
    current_change_type: Option<OSMObjectChangeType>,
    old: Option<OSMObject>,
    new: Option<OSMObject>,
    in_remark: bool,
}

impl<T: Read> OSMObjectChangeIterator<T> {
    pub fn new(readable: T) -> Self {
        let mut reader = Reader::from_reader(BufReader::new(readable));
        reader.trim_text(true).expand_empty_elements(true);
        OSMObjectChangeIterator {
            reader,
            finished: false,
            current_event: None,
            current_change_type: None,
            old: None,
            new: None,
            in_remark: false,
        }
    }

    fn parse_object(&mut self) -> Result<OSMObject> {
        trace!("Parse object called.");
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
            f64::from(0),
            f64::from(0),
        );
        let mut buf = vec![];
        loop {
            let event = self.reader.read_event_into(&mut buf);
            let event = event?;
            match event {
                Event::Start(tag) => {
                    trace!(
                        "Start of element {:?} with attributes {:?} during object parsing.",
                        tag.local_name(),
                        tag.attributes_raw()
                    );
                    let mut attrs = convert_to_map(tag.attributes())?;
                    match tag.local_name().as_ref() {
                        b"node" | b"way" | b"relation" => {
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
                        b"tag" => {
                            tags.insert(
                                attrs.remove("k").expect("No k in attrs"),
                                attrs.remove("v").expect("No v in attrs."),
                            );
                        }
                        b"nd" => nodes.push(
                            attrs["ref"]
                                .parse()
                                .expect("Could not parse node ref as an u64."),
                        ),
                        b"member" => members.push(OSMRelationMember::new(
                            attrs["ref"]
                                .parse()
                                .expect("Could not parse member ref as an u64."),
                            OSMObjectType::from_str(&attrs["type"])
                                .expect("Could not parse referenced object type."),
                            attrs.remove("role").expect("No role in attrs."),
                        )),
                        _ => panic!("Unexpected start of element {:?}.", tag.local_name()),
                    }
                }
                Event::End(tag) => {
                    trace!(
                        "End of {:?} element during object parsing.",
                        tag.local_name()
                    );
                    match tag.local_name().as_ref() {
                        b"node" => {
                            return Ok(OSMObject::new_node(
                                id, timestamp, version, changeset, user, uid, tags, lat, lon,
                            ));
                        }
                        b"way" => {
                            return Ok(OSMObject::new_way(
                                id, timestamp, version, changeset, user, uid, tags, nodes,
                            ));
                        }
                        b"relation" => {
                            return Ok(OSMObject::new_rel(
                                id, timestamp, version, changeset, user, uid, tags, members,
                            ));
                        }
                        b"tag" | b"nd" | b"member" => {}
                        _ => panic!("Unexpected end of element {:?}.", tag.local_name()),
                    }
                }
                event => panic!("Unexpected event during xml parsing: {event:?}."),
            }
        }
    }

    fn parse_change_step(&mut self) -> Result<()> {
        let mut buf = vec![];
        trace!("Doing a parse change step.");
        match self.reader.read_event_into(&mut buf) {
            Ok(Event::Decl(_)) => trace!("Start document."),
            Ok(Event::Text(chars)) => {
                trace!("Characters: {}", chars.unescape()?);
                if self.in_remark {
                    self.current_event =
                        Some(OSMObjectChangeEvent::Remark(chars.unescape()?.to_string()));
                }
            }
            Ok(Event::Eof) => {
                trace!("End document.");
                self.finished = true;
            }
            Ok(Event::Start(tag) | Event::Empty(tag)) => {
                trace!(
                    "Start of an element with name {:?} and attributes {:?}.",
                    tag.local_name(),
                    tag.attributes_raw()
                );
                match tag.local_name().as_ref() {
                    b"action" => {
                        self.current_event = None;
                        let attrs = convert_to_map(tag.attributes())?;
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
                    b"new" => self.new = Some(self.parse_object()?),
                    b"old" => self.old = Some(self.parse_object()?),
                    b"remark" => self.in_remark = true,
                    b"osm" | b"note" | b"meta" => {}
                    _ => panic!("Start of unexpected tag {:?}.", tag.local_name()),
                }
            }
            Ok(Event::End(tag)) => {
                trace!("End of element with name {:?}.", tag.local_name());
                match tag.local_name().as_ref() {
                    b"action" => {
                        self.current_event = Some(OSMObjectChangeEvent::Change(OSMObjectChange {
                            change_type: self
                                .current_change_type
                                .take()
                                .expect("Did not set change type?"),
                            old: self.old.take(),
                            new: self.new.take(),
                        }))
                    }
                    b"osm3response" => self.finished = true,
                    b"remark" => self.in_remark = false,
                    b"note" | b"osm" | b"meta" | b"old" | b"new" => {}
                    _ => panic!("Unexpected end of {:?}.", tag.local_name()),
                }
            }
            Err(e) => {
                self.finished = true;
                return Err(Error::from(e));
            }
            event => panic!("Unexpected event during parsing: {event:?}"),
        }
        Ok(())
    }
}

impl<T: Read> Iterator for OSMObjectChangeIterator<T> {
    type Item = Result<OSMObjectChangeEvent>;

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
                    if self.current_event.is_some() {
                        return Some(Ok(self.current_event.take()?));
                    }
                }
            }
        }
    }
}
