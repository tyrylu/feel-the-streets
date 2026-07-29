use geo::{Geodesic, Point};
use pyo3::prelude::*;

const EARTH_RADIUS_M: f64 = 6_371_000.0;

/// Geodesic (Karney) distance in metres between two (lat, lon) points.
#[pyfunction]
pub fn geodesic_distance(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
    use geo::Distance;
    Geodesic.distance(Point::new(lon1, lat1), Point::new(lon2, lat2))
}

/// Initial geodesic (Karney) bearing in degrees from point 1 to point 2.
#[pyfunction]
pub fn geodesic_bearing(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
    use geo::Bearing;
    Geodesic.bearing(Point::new(lon1, lat1), Point::new(lon2, lat2))
}

/// Returns `(distance_m, initial_bearing_deg, final_bearing_deg)` between two points,
/// using Karney geodesics. Replaces pygeodesy's `LatLon.distanceTo3()`.
#[pyfunction]
pub fn geodesic_distance_and_bearings(
    lat1: f64,
    lon1: f64,
    lat2: f64,
    lon2: f64,
) -> (f64, f64, f64) {
    use geo::{Bearing, Distance};
    let p1 = Point::new(lon1, lat1);
    let p2 = Point::new(lon2, lat2);
    let dist = Geodesic.distance(p1, p2);
    let initial = Geodesic.bearing(p1, p2);
    // Final bearing = reverse bearing from p2 to p1, rotated 180°.
    let final_bearing = (Geodesic.bearing(p2, p1) + 180.0) % 360.0;
    (dist, initial, final_bearing)
}

/// Returns `(new_lat, new_lon)` after travelling `distance` metres at `bearing` degrees
/// from `(lat, lon)`, using Karney geodesics.
#[pyfunction]
pub fn geodesic_destination(lat: f64, lon: f64, distance: f64, bearing: f64) -> (f64, f64) {
    use geo::Destination;
    let dest = Geodesic.destination(Point::new(lon, lat), bearing, distance);
    (dest.y(), dest.x())
}

/// Returns `(new_lat, new_lon, final_bearing_deg)` after travelling `distance` metres at
/// `bearing` degrees from `(lat, lon)`. Replaces pygeodesy's `LatLon.destination2()`.
#[pyfunction]
pub fn geodesic_destination2(
    lat: f64,
    lon: f64,
    distance: f64,
    bearing: f64,
) -> (f64, f64, f64) {
    use geo::{Bearing, Destination};
    let origin = Point::new(lon, lat);
    let dest = Geodesic.destination(origin, bearing, distance);
    // Final bearing at the destination.
    let final_bearing = (Geodesic.bearing(dest, origin) + 180.0) % 360.0;
    (dest.y(), dest.x(), final_bearing)
}

/// Geodesic area of a polygon ring given as a list of `(lon, lat)` coordinate pairs, in m².
/// Uses the Karney (2013) algorithm via `geo::GeodesicArea`.
/// Pass the exterior ring, then subtract any interior rings individually.
#[pyfunction]
pub fn geodesic_area(coords: Vec<(f64, f64)>) -> f64 {
    use geo::GeodesicArea;
    if coords.len() < 3 {
        return 0.0;
    }
    let ls: geo::LineString<f64> = coords
        .iter()
        .map(|&(x, y)| geo::coord! { x: x, y: y })
        .collect();
    let polygon = geo::Polygon::new(ls, vec![]);
    polygon.geodesic_area_signed().abs()
}

/// Project `(lat, lon)` to local flat (easting, northing) in metres, relative to a
/// reference origin `(ref_lat, ref_lon)`.
///
/// Uses an equirectangular (plate carrée) projection with the origin's latitude as the
/// standard parallel, so distances and angles near the origin are accurate.
/// Suitable for city-scale 3D audio positioning.
#[pyfunction]
pub fn equirectangular_project(
    lat: f64,
    lon: f64,
    ref_lat: f64,
    ref_lon: f64,
) -> (f64, f64) {
    let easting = (lon - ref_lon).to_radians() * ref_lat.to_radians().cos() * EARTH_RADIUS_M;
    let northing = (lat - ref_lat).to_radians() * EARTH_RADIUS_M;
    (easting, northing)
}
