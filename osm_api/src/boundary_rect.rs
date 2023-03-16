
#[derive(Debug)]
pub struct BoundaryRect {
    pub min_x: f64,
    pub min_y: f64,
    pub max_x: f64,
    pub max_y: f64
}

impl BoundaryRect {
    
    pub fn whole_world() -> Self {
        Self {
            min_x: -180.0,
            min_y: -180.0,
            max_x: 180.0,
            max_y: 180.0
        }
    }

    pub(crate) fn contains_point(&self, x: f64, y: f64) -> bool {
        self.min_x <= x && self.max_x >= x && self.min_y <= y && self.max_y >= y
    }

    pub fn as_wkb_polygon(&self) -> Vec<u8> {
        // It's a little-endian
        let mut ret = vec![1_u8];
        // Polygon
        ret.extend(3_u32.to_le_bytes());
        // It has one ring
        ret.extend(1_u32.to_le_bytes());
        // With 5 points
        ret.extend(5_u32.to_le_bytes());
        // Bottom left
        ret.extend(self.min_x.to_le_bytes());
        ret.extend(self.min_y.to_le_bytes());
        // Bottom right
        ret.extend(self.max_x.to_le_bytes());
        ret.extend(self.min_y.to_le_bytes());
        // Top right
        ret.extend(self.max_x.to_le_bytes());
        ret.extend(self.max_y.to_le_bytes());
        // Top left
        ret.extend(self.min_x.to_le_bytes());
        ret.extend(self.max_y.to_le_bytes());
        // And, finally, bottom left again
        ret.extend(self.min_x.to_le_bytes());
        ret.extend(self.min_y.to_le_bytes());
        ret
    }
}