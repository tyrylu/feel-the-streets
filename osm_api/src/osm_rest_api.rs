use crate::object::OSMObject;
use crate::raw_object::{OSMObject as RawOSMObject, OSMObjectOrRemark};
use crate::{Error, Result};
use itertools::Itertools;
use log::debug;
use once_cell::sync::Lazy;
use quick_xml::de::Deserializer;
use serde::Deserialize;
use smol_str::SmolStr;
use std::io::BufRead;
use std::io::BufReader;
use ureq::Agent;

const OSM_API_BASE: &str = "https://api.openstreetmap.org/api/0.6";
/// Safe batch size: 700 × 11 chars ("12345678901,") = ~7700 chars, well under the 8207 limit.
const BATCH_SIZE: usize = 700;

static AGENT: Lazy<Agent> = Lazy::new(|| {
    Agent::new_with_config(
        Agent::config_builder()
            .user_agent("feel-the-streets/1.0")
            .build(),
    )
});

fn type_plural(prefix: char) -> &'static str {
    match prefix {
        'n' => "nodes",
        'w' => "ways",
        'r' => "relations",
        _ => unreachable!(),
    }
}

fn parse_osm_xml_response(body: impl std::io::Read) -> Result<Vec<OSMObject>> {
    let mut reader = BufReader::with_capacity(65536, body);
    let mut line = String::new();
    // Skip XML declaration and <osm ...> opening tag.
    // Unlike Overpass, the OSM REST API has no <note> or <meta> lines.
    for _ in 0..2 {
        reader.read_line(&mut line)?;
    }
    let mut de = Deserializer::from_reader(reader);
    let mut objects = Vec::new();
    while let Ok(obj) = OSMObjectOrRemark::deserialize(&mut de) {
        let raw: RawOSMObject = match obj.try_into() {
            Ok(r) => r,
            Err(Error::OverpassAPIError(msg)) => {
                // Defensive: handle <remark> elements if they ever appear.
                debug!("OSM API message element: {msg}");
                continue;
            }
            Err(e) => return Err(e),
        };
        let internal: OSMObject = raw.try_into()?;
        objects.push(internal);
    }
    Ok(objects)
}

pub fn fetch_objects_by_ids(ids: &mut [SmolStr]) -> Result<Vec<OSMObject>> {
    if ids.is_empty() {
        return Ok(vec![]);
    }
    ids.sort_unstable_by_key(|id| id.chars().next());
    let mut results = Vec::with_capacity(ids.len());

    for (prefix, group) in &ids
        .iter()
        .chunk_by(|id| id.chars().next().unwrap())
    {
        let numeric_ids: Vec<&str> = group.map(|id| &id.as_str()[1..]).collect();
        let type_p = type_plural(prefix);

        for chunk in numeric_ids.chunks(BATCH_SIZE) {
            let ids_str = chunk.join(",");
            let url = format!("{OSM_API_BASE}/{type_p}");
            debug!(
                "Fetching {} {type_p} from OSM REST API",
                chunk.len()
            );
            let resp = AGENT
                .get(&url)
                .query(type_p, &ids_str)
                .call()?;
            let objects = parse_osm_xml_response(resp.into_body().into_reader())?;
            results.extend(objects);
        }
    }

    Ok(results)
}
