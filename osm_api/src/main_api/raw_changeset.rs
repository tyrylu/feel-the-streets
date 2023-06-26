use crate::raw_object::Tag;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub(crate) struct RawChangesets {
    #[serde(rename = "changeset")]
    pub(crate) changesets: Vec<RawChangeset>,
}

#[derive(Debug, Deserialize)]
pub struct RawChangeset {
    #[serde(rename = "@id")]
    pub(crate) id: u64,
    #[serde(rename = "@created_at")]
    pub(crate) created_at: String,
    #[serde(rename = "@closed_at")]
    pub(crate) closed_at: Option<String>,
    #[serde(rename = "@open")]
    pub(crate) is_open: bool,
    #[serde(rename = "@user")]
    pub(crate) user: String,
    #[serde(rename = "@uid")]
    pub(crate) uid: u64,
    #[serde(rename = "@min_lat")]
    pub(crate) min_lat: Option<f64>,
    #[serde(rename = "@min_lon")]
    pub(crate) min_lon: Option<f64>,
    #[serde(rename = "@max_lat")]
    pub(crate) max_lat: Option<f64>,
    #[serde(rename = "@max_lon")]
    pub(crate) max_lon: Option<f64>,
    #[serde(rename = "@changes_count")]
    pub(crate) changes_count: u32,
    #[serde(rename = "@comments_count")]
    pub(crate) comments_count: u32,
    #[serde(default, rename = "tag")]
    pub(crate) tags: Vec<Tag>,
}
