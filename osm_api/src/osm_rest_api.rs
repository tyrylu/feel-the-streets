/// Client for the OSM REST API v0.6 (api.openstreetmap.org).
///
/// Used as an alternative to Overpass for current-data queries, which avoids
/// Overpass rate limits during ongoing change processing.
use crate::object::OSMObject;
use crate::raw_object::{OSMObject as RawOSMObject, OSMObjectOrRemark};
use crate::{Error, Result};
use itertools::Itertools;
use log::{debug, info};
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

/// Parse a standard OSM API XML response body into a list of `OSMObject`s.
///
/// The OSM API returns:
/// ```xml
/// <?xml version="1.0" encoding="UTF-8"?>
/// <osm version="0.6" ...>
///   <node .../>
///   ...
/// </osm>
/// ```
/// Unlike the Overpass response there is no `<note>` or `<meta>` line,
/// so we only skip the XML declaration and the `<osm>` opening tag (2 lines).
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

/// Fetch multiple OSM objects by their prefixed IDs (e.g. `"n123"`, `"w456"`, `"r789"`).
///
/// Objects are batched by type and sent as multi-fetch GET requests to the OSM REST API.
/// Only current (latest) versions are returned; this must not be used for historical queries.
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
            info!(
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

/// Fetch all relations that contain the given relation ID as a member.
///
/// Equivalent to the Overpass query `rel(<id>);<<` but uses the OSM REST API.
/// Returns current (not historical) data.
pub fn fetch_parent_relations(relation_id: u64) -> Result<Vec<OSMObject>> {
    let url = format!("{OSM_API_BASE}/relation/{relation_id}/relations");
    info!("Fetching parent relations of r{relation_id} from OSM REST API");
    let resp = AGENT.get(&url).call()?;
    parse_osm_xml_response(resp.into_body().into_reader())
}
