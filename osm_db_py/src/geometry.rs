use geo::{coord, Geometry, LineString};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use std::sync::Arc;

/// A parsed geometry object, backed by an Arc so it can be cheaply cloned out of the cache.
#[pyclass(name = "Geometry")]
pub struct PyGeometry {
    pub(crate) inner: Arc<Geometry<f64>>,
}

impl PyGeometry {
    pub fn new(geom: Arc<Geometry<f64>>) -> Self {
        Self { inner: geom }
    }

    pub fn from_geo(geom: Geometry<f64>) -> Self {
        Self {
            inner: Arc::new(geom),
        }
    }
}

#[pymethods]
impl PyGeometry {
    /// Construct a LineString geometry from a list of (x, y) / (lon, lat) coordinate pairs.
    #[staticmethod]
    pub fn from_linestring(coords: Vec<(f64, f64)>) -> Self {
        let ls: LineString<f64> = coords.iter().map(|&(x, y)| coord! { x: x, y: y }).collect();
        Self::from_geo(Geometry::LineString(ls))
    }

    /// Returns the geometry type as a string: "Point", "LineString", "Polygon",
    /// "MultiPoint", "MultiLineString", "MultiPolygon", "GeometryCollection".
    pub fn geom_type(&self) -> &str {
        match self.inner.as_ref() {
            Geometry::Point(_) => "Point",
            Geometry::Line(_) => "LineString",
            Geometry::LineString(_) => "LineString",
            Geometry::Polygon(_) => "Polygon",
            Geometry::MultiPoint(_) => "MultiPoint",
            Geometry::MultiLineString(_) => "MultiLineString",
            Geometry::MultiPolygon(_) => "MultiPolygon",
            Geometry::GeometryCollection(_) => "GeometryCollection",
            Geometry::Rect(_) => "Polygon",
            Geometry::Triangle(_) => "Polygon",
        }
    }

    /// True if the geometry has no coordinates.
    pub fn is_empty(&self) -> bool {
        use geo::HasDimensions;
        self.inner.is_empty()
    }

    /// True if the LineString's first and last coordinates are equal.
    /// Returns False for non-LineString geometries.
    pub fn is_closed(&self) -> bool {
        match self.inner.as_ref() {
            Geometry::LineString(ls) => ls.is_closed(),
            _ => false,
        }
    }

    /// Returns the coordinates as a list of (x, y) tuples.
    /// For Point: single-element list.
    /// For LineString: all vertices.
    /// For other types, raises ValueError — use exterior_coords/interior_rings/parts.
    pub fn coords(&self) -> PyResult<Vec<(f64, f64)>> {
        match self.inner.as_ref() {
            Geometry::Point(p) => Ok(vec![(p.x(), p.y())]),
            Geometry::Line(l) => Ok(vec![(l.start.x, l.start.y), (l.end.x, l.end.y)]),
            Geometry::LineString(ls) => Ok(ls.coords().map(|c| (c.x, c.y)).collect()),
            _ => Err(PyValueError::new_err(
                "coords() is only supported for Point and LineString geometries; \
                 use exterior_coords(), interior_rings(), or parts() for other types",
            )),
        }
    }

    /// Convenience accessor for a Point geometry: returns (x, y) / (lon, lat).
    pub fn point_coords(&self) -> PyResult<(f64, f64)> {
        match self.inner.as_ref() {
            Geometry::Point(p) => Ok((p.x(), p.y())),
            _ => Err(PyValueError::new_err(
                "point_coords() is only supported for Point geometries",
            )),
        }
    }

    /// Returns the exterior ring coordinates of a Polygon as a list of (x, y) tuples.
    pub fn exterior_coords(&self) -> PyResult<Vec<(f64, f64)>> {
        match self.inner.as_ref() {
            Geometry::Polygon(p) => Ok(p.exterior().coords().map(|c| (c.x, c.y)).collect()),
            Geometry::Rect(r) => Ok(r
                .to_polygon()
                .exterior()
                .coords()
                .map(|c| (c.x, c.y))
                .collect()),
            Geometry::Triangle(t) => Ok(t
                .to_polygon()
                .exterior()
                .coords()
                .map(|c| (c.x, c.y))
                .collect()),
            _ => Err(PyValueError::new_err(
                "exterior_coords() is only supported for Polygon geometries",
            )),
        }
    }

    /// Returns the interior rings (holes) of a Polygon as a list of lists of (x, y) tuples.
    pub fn interior_rings(&self) -> PyResult<Vec<Vec<(f64, f64)>>> {
        match self.inner.as_ref() {
            Geometry::Polygon(p) => Ok(p
                .interiors()
                .iter()
                .map(|ring| ring.coords().map(|c| (c.x, c.y)).collect())
                .collect()),
            Geometry::Rect(_) | Geometry::Triangle(_) => Ok(vec![]),
            _ => Err(PyValueError::new_err(
                "interior_rings() is only supported for Polygon geometries",
            )),
        }
    }

    /// Returns the sub-geometries of a GeometryCollection or Multi* geometry
    /// as a list of Geometry objects.
    pub fn parts(&self) -> PyResult<Vec<PyGeometry>> {
        match self.inner.as_ref() {
            Geometry::GeometryCollection(gc) => Ok(gc
                .iter()
                .map(|g| PyGeometry::from_geo(g.clone()))
                .collect()),
            Geometry::MultiPolygon(mp) => Ok(mp
                .iter()
                .map(|p| PyGeometry::from_geo(Geometry::Polygon(p.clone())))
                .collect()),
            Geometry::MultiLineString(mls) => Ok(mls
                .iter()
                .map(|ls| PyGeometry::from_geo(Geometry::LineString(ls.clone())))
                .collect()),
            Geometry::MultiPoint(mp) => Ok(mp
                .iter()
                .map(|p| PyGeometry::from_geo(Geometry::Point(*p)))
                .collect()),
            _ => Err(PyValueError::new_err(
                "parts() is only supported for GeometryCollection and Multi* geometries",
            )),
        }
    }
}

/// Parse raw WKB bytes into a geo::Geometry. Panics if the bytes are invalid WKB
/// (the DB should only ever produce valid WKB).
pub fn parse_wkb(bytes: &[u8]) -> Geometry<f64> {
    use geo_traits::to_geo::ToGeoGeometry;
    let geom_wkb = wkb::reader::read_wkb(bytes).expect("invalid WKB in entity cache");
    geom_wkb.to_geometry()
}
