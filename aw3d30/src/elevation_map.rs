use crate::coordinate_ops::DEGREE_PER_PIXEL;
use crate::Result;
use bincode::{Decode, Encode};
use std::io::Cursor;

#[derive(Decode, Encode)]
pub struct ElevationMap {
    pub(crate) origin_lat: f64,
    pub(crate) origin_lon: f64,
    pub(crate) width: u32,
    pub(crate) height: u32,
    pub(crate) data: Vec<i16>,
}

impl ElevationMap {
    pub fn elevation_at_coords(&self, lat: f64, lon: f64) -> Option<f64> {
        self.bicubic_interpolation(lat, lon)
    }

    fn elevation_of_square(&self, lat: f64, lon: f64) -> Option<i16> {
        let x = ((lon - self.origin_lon) / DEGREE_PER_PIXEL) as u32;
        let y = ((self.origin_lat - lat) / DEGREE_PER_PIXEL) as u32;
        if x >= self.width || y >= self.height {
            return None;
        }
        Some(self.data[(y * self.width + x) as usize])
    }

    fn cubic_weight(t: f64) -> f64 {
        let a = -0.5; // This can be adjusted for different smoothness
        let t_abs = t.abs();

        if t_abs <= 1.0 {
            (a + 2.0) * t_abs.powi(3) - (a + 3.0) * t_abs.powi(2) + 1.0
        } else if t_abs <= 2.0 {
            a * t_abs.powi(3) - 5.0 * a * t_abs.powi(2) + 8.0 * a * t_abs - 4.0 * a
        } else {
            0.0
        }
    }

    fn bilinear_interpolation(&self, lat: f64, lon: f64) -> Option<f64> {
        let x_float = (lon - self.origin_lon) / DEGREE_PER_PIXEL;
        let y_float = (self.origin_lat - lat) / DEGREE_PER_PIXEL;

        let x = x_float.floor() as u32;
        let y = y_float.floor() as u32;

        if x + 1 >= self.width || y + 1 >= self.height {
            return self.elevation_of_square(lat, lon).map(|v| v as f64);
        }

        let x_ratio = x_float - x as f64;
        let y_ratio = y_float - y as f64;

        let index = |x, y| (y * self.width + x) as usize;

        let val1 = self.data[index(x, y)] as f64;
        let val2 = self.data[index(x + 1, y)] as f64;
        let val3 = self.data[index(x, y + 1)] as f64;
        let val4 = self.data[index(x + 1, y + 1)] as f64;

        let result = ((1.0 - x_ratio) * (1.0 - y_ratio) * val1)
            + (x_ratio * (1.0 - y_ratio) * val2)
            + ((1.0 - x_ratio) * y_ratio * val3)
            + (x_ratio * y_ratio * val4);

        Some(result)
    }

    fn bicubic_interpolation(&self, lat: f64, lon: f64) -> Option<f64> {
        let x_float = (lon - self.origin_lon) / DEGREE_PER_PIXEL;
        let y_float = (self.origin_lat - lat) / DEGREE_PER_PIXEL;

        let x = x_float.floor() as i32;
        let y = y_float.floor() as i32;

        // Attempt bilinear interpolation at edges
        if x < 1 || y < 1 || x + 2 >= self.width as i32 || y + 2 >= self.height as i32 {
            return self.bilinear_interpolation(lat, lon);
        }

        let mut interpolated_value = 0.0;
        for i in -1..=2 {
            for j in -1..=2 {
                let weight = Self::cubic_weight(i as f64 - (x_float - x as f64))
                    * Self::cubic_weight(j as f64 - (y_float - y as f64));
                interpolated_value += weight
                    * self.data[(y + j) as usize * self.width as usize + (x + i) as usize] as f64;
            }
        }

        Some(interpolated_value)
    }

    pub fn serialize(&self) -> Result<Vec<u8>> {
        let data = bincode::encode_to_vec(self, bincode::config::legacy())?;
        let dest = zstd::encode_all(Cursor::new(data), 22)?;
        Ok(dest)
    }

    pub fn from_serialized(data: &[u8]) -> Result<Self> {
        let decompressed = zstd::decode_all(Cursor::new(data))?;
        Ok(bincode::decode_from_slice(&decompressed, bincode::config::legacy())?.0)
    }
}
