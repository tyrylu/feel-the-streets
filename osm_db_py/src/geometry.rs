use geo::{coord, Geometry, LineString, Point};
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

    /// Returns a representative interior point of any geometry as (x, y) / (lon, lat).
    pub fn representative_point(&self) -> PyResult<(f64, f64)> {
        use geo::InteriorPoint;
        let pt: Option<Point<f64>> = self.inner.interior_point();
        pt.map(|p| (p.x(), p.y()))
            .ok_or_else(|| PyValueError::new_err("geometry has no interior point (is it empty?)"))
    }

    /// Returns the (x, y) / (lon, lat) of the closest point on this geometry to the given point.
    /// Uses planar (Euclidean) distance — correct for relative comparisons within a city area.
    pub fn closest_point(&self, x: f64, y: f64) -> PyResult<(f64, f64)> {
        use geo::ClosestPoint;
        let query = Point::new(x, y);
        let result = match self.inner.as_ref() {
            Geometry::Point(p) => geo::Closest::SinglePoint(*p),
            Geometry::Line(l) => l.closest_point(&query),
            Geometry::LineString(ls) => ls.closest_point(&query),
            Geometry::Polygon(p) => p.closest_point(&query),
            Geometry::MultiPoint(mp) => mp.closest_point(&query),
            Geometry::MultiLineString(mls) => mls.closest_point(&query),
            Geometry::MultiPolygon(mp) => mp.closest_point(&query),
            Geometry::GeometryCollection(gc) => gc.closest_point(&query),
            Geometry::Rect(r) => r.to_polygon().closest_point(&query),
            Geometry::Triangle(t) => t.to_polygon().closest_point(&query),
        };
        match result {
            geo::Closest::SinglePoint(p) | geo::Closest::Intersection(p) => Ok((p.x(), p.y())),
            geo::Closest::Indeterminate => Err(PyValueError::new_err(
                "closest_point: result is indeterminate (degenerate geometry?)",
            )),
        }
    }

    /// Returns the planar (Euclidean) distance from this geometry to a point (x, y).
    /// Used for finding the closest line segment — only relative ordering matters.
    pub fn euclidean_distance_to_point(&self, x: f64, y: f64) -> f64 {
        use geo::Distance;
        use geo::Euclidean;
        let query = Point::new(x, y);
        match self.inner.as_ref() {
            Geometry::Point(p) => Euclidean.distance(p, &query),
            Geometry::Line(l) => Euclidean.distance(l, &query),
            Geometry::LineString(ls) => Euclidean.distance(ls, &query),
            Geometry::Polygon(p) => Euclidean.distance(p, &query),
            Geometry::MultiPoint(mp) => Euclidean.distance(mp, &query),
            Geometry::MultiLineString(mls) => Euclidean.distance(mls, &query),
            Geometry::MultiPolygon(mp) => Euclidean.distance(mp, &query),
            Geometry::GeometryCollection(gc) => {
                gc.iter()
                    .map(|g| PyGeometry::from_geo(g.clone()).euclidean_distance_to_point(x, y))
                    .fold(f64::INFINITY, f64::min)
            }
            Geometry::Rect(r) => {
                let p = r.to_polygon();
                Euclidean.distance(&p, &query)
            }
            Geometry::Triangle(t) => {
                let p = t.to_polygon();
                Euclidean.distance(&p, &query)
            }
        }
    }

    /// Returns true if this geometry spatially contains the other geometry.
    pub fn contains(&self, other: &PyGeometry) -> bool {
        use geo::Contains;
        // geo::Contains is only implemented for certain type pairs; dispatch manually.
        match (self.inner.as_ref(), other.inner.as_ref()) {
            (Geometry::Polygon(a), Geometry::Point(b)) => a.contains(b),
            (Geometry::Polygon(a), Geometry::LineString(b)) => a.contains(b),
            (Geometry::Polygon(a), Geometry::Polygon(b)) => a.contains(b),
            (Geometry::MultiPolygon(a), Geometry::Point(b)) => a.contains(b),
            (Geometry::MultiPolygon(a), Geometry::LineString(b)) => a.contains(b),
            (Geometry::LineString(a), Geometry::Point(b)) => a.contains(b),
            // For any other combination fall back to bounding-box containment as a best-effort.
            _ => {
                use geo::BoundingRect;
                let bbox_self = self.inner.bounding_rect();
                let bbox_other = other.inner.bounding_rect();
                match (bbox_self, bbox_other) {
                    (Some(a), Some(b)) => {
                        a.min().x <= b.min().x
                            && a.min().y <= b.min().y
                            && a.max().x >= b.max().x
                            && a.max().y >= b.max().y
                    }
                    _ => false,
                }
            }
        }
    }

    /// Computes the intersection of two geometries.
    ///
    /// For LineString × LineString (the road-crossing use case) this returns a Point
    /// geometry at the first intersection found, or an empty geometry collection if
    /// the lines do not intersect.
    ///
    /// For Polygon types this delegates to geo's BooleanOps.
    pub fn intersection(&self, other: &PyGeometry) -> PyResult<PyGeometry> {
        use geo::line_intersection::{line_intersection, LineIntersection};

        // Extract all Line segments from a geometry (LineString or Line).
        fn extract_lines(g: &Geometry<f64>) -> Vec<geo::Line<f64>> {
            match g {
                Geometry::LineString(ls) => ls.lines().collect(),
                Geometry::Line(l) => vec![*l],
                _ => vec![],
            }
        }

        match (self.inner.as_ref(), other.inner.as_ref()) {
            // LineString × LineString — find the first point intersection.
            (
                Geometry::LineString(_) | Geometry::Line(_),
                Geometry::LineString(_) | Geometry::Line(_),
            ) => {
                let lines_a = extract_lines(self.inner.as_ref());
                let lines_b = extract_lines(other.inner.as_ref());
                for seg_a in &lines_a {
                    for seg_b in &lines_b {
                        if let Some(result) = line_intersection(*seg_a, *seg_b) {
                            let pt = match result {
                                LineIntersection::SinglePoint { intersection, .. } => {
                                    intersection
                                }
                                LineIntersection::Collinear { intersection } => {
                                    intersection.start_point().into()
                                }
                            };
                            return Ok(PyGeometry::from_geo(Geometry::Point(Point::from(pt))));
                        }
                    }
                }
                // No intersection found — return an empty GeometryCollection.
                Ok(PyGeometry::from_geo(Geometry::GeometryCollection(
                    geo::GeometryCollection::default(),
                )))
            }
            // Polygon × Polygon — use BooleanOps.
            (Geometry::Polygon(a), Geometry::Polygon(b)) => {
                use geo::BooleanOps;
                let result = a.intersection(b);
                Ok(PyGeometry::from_geo(Geometry::MultiPolygon(result)))
            }
            (Geometry::MultiPolygon(a), Geometry::MultiPolygon(b)) => {
                use geo::BooleanOps;
                let result = a.intersection(b);
                Ok(PyGeometry::from_geo(Geometry::MultiPolygon(result)))
            }
            _ => Err(PyValueError::new_err(format!(
                "intersection() not supported between {} and {}",
                self.geom_type(),
                other.geom_type()
            ))),
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
