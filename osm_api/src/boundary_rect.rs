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
}