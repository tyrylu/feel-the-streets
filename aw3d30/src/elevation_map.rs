use crate::coordinate_ops::DEGREE_PER_PIXEL;
use serde::{Serialize, Deserialize};
use crate::Result;
use std::io::Cursor;

#[derive(Serialize, Deserialize)]
pub struct ElevationMap {
    pub(crate) origin_lat: f64,
    pub(crate) origin_lon: f64,
    pub(crate) width: u32,
    pub(crate) height: u32,
    pub(crate) data: Vec<i16>,
}

impl ElevationMap {
    pub fn elevation_at_coords(&self, lat: f64, lon: f64) -> Option<i16> {
        let x = ((lon - self.origin_lon) / DEGREE_PER_PIXEL) as u32;
        let y = ((self.origin_lat - lat) / DEGREE_PER_PIXEL) as u32;
        if x >= self.width || y >= self.height {
            return None;
        }
        Some(self.data[(y * self.width + x) as usize])
    }

    pub fn serialize(&self) -> Result<Vec<u8>> {
        let data = bincode::serialize(self)?;
        let dest = zstd::encode_all(Cursor::new(data), 22)?;
        Ok(dest)
    }

    pub fn from_serialized(data: &[u8]) -> Result<Self> {
        let decompressed = zstd::decode_all(Cursor::new(data))?;
        Ok(bincode::deserialize(&decompressed)?)
    }
}