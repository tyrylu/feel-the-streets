use osm_api::changeset::Changeset as ApiChangeset;
use osm_api::BoundaryRect;

pub struct InsertableChangeset {
    pub id: u32,
    pub min_lat: f64,
    pub max_lat: f64,
    pub min_lon: f64,
    pub max_lon: f64,
}

pub(crate) struct Changeset {
    pub id: u32,
    pub batch: u32,
    pub bounds: BoundaryRect,
}

impl From<ApiChangeset> for InsertableChangeset {
    fn from(changeset: ApiChangeset) -> Self {
        let bounds = changeset.bounds.expect("Changeset has no bounds");
        Self {
            id: changeset.id,
            min_lat: bounds.min_y,
            max_lat: bounds.max_y,
            min_lon: bounds.min_x,
            max_lon: bounds.max_x,
        }
    }
}
