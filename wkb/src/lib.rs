//! This crate provides functions to convert `rust-geo` geometry types to and from Well Known
//! Binary format.
//!
//! # Examples
//!
//! ```rust
//! # extern crate geo_types;
//! # extern crate wkb;
//! # fn main() {
//! use geo_types::*;
//! use wkb::*;
//!
//! let p: Geometry<f64> = Geometry::Point(Point::new(2., 4.));
//! let res = geom_to_wkb(&p);
//! assert_eq!(res, vec![1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 16, 64]);
//! # }
//! ```
//!
//! You can also 'read' a Geometry from a `std::io::Read`:
//!
//! ```rust
//! # extern crate geo_types;
//! # extern crate wkb;
//! # fn main() {
//! use geo_types::*;
//! use wkb::*;
//!
//! let bytes: Vec<u8> = vec![1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 0, 0, 0, 0, 0, 0, 16, 64];
//! let p: Geometry<f64> = wkb_to_geom(&mut bytes.as_slice()).unwrap();
//! assert_eq!(p, Geometry::Point(Point::new(2., 4.)));
//! # }
//! ```
//!
//! Adding proper `*Ext` traits is planned.
//!
//!

#![allow(unused_must_use)]
extern crate geo_types;
extern crate byteorder;
extern crate num_traits;

use std::io::prelude::*;
use std::io;

use geo_types::*;
use num_traits::Float;
use byteorder::{WriteBytesExt, ReadBytesExt};
use byteorder::{LittleEndian};

#[derive(Debug)]
pub enum WKBReadError {
    WrongType,
    IOError(io::Error),
}

impl From<io::Error> for WKBReadError {
    fn from(err: io::Error) -> WKBReadError {
        WKBReadError::IOError(err)
    }
}


fn read_point<I: Read>(mut wkb: I) -> Result<Coordinate<f64>, WKBReadError> {
    let x: f64 = wkb.read_f64::<LittleEndian>()?;
    let y: f64 = wkb.read_f64::<LittleEndian>()?;
    Ok(Coordinate{ x, y })
}

fn write_point<W: Write, T: Into<f64>+Float>(c: &Coordinate<T>, out: &mut W) {
    out.write_f64::<LittleEndian>(c.x.into());
    out.write_f64::<LittleEndian>(c.y.into());
}

fn read_many_points<I: Read>(mut wkb: I) -> Result<Vec<Coordinate<f64>>, WKBReadError> {
    let num_points = wkb.read_u32::<LittleEndian>()? as usize;
    let mut res: Vec<Coordinate<f64>> = Vec::with_capacity(num_points);
    for _ in 0..num_points {
        res.push(read_point(&mut wkb)?);
    }

    Ok(res)
}

fn write_many_points<W: Write, T: Into<f64>+Float>(mp: &[Coordinate<T>], mut out: &mut W) {
    out.write_u32::<LittleEndian>(mp.len() as u32);
    for p in mp.iter() {
        write_point(p, &mut out);
    }
}

/// Convert a Geometry into WKB bytes.
pub fn geom_to_wkb<T: Into<f64>+Float>(geom: &Geometry<T>) -> Vec<u8> {
    let mut result: Vec<u8> = Vec::new();
    write_geom_to_wkb(geom, &mut result);
    result
}




/// Write a geometry to the underlying writer, except for the endianity byte.
pub fn write_geom_to_wkb<W: Write, T: Into<f64>+Float>(geom: &Geometry<T>, mut result: &mut W) {
    // FIXME replace type signature with Into<Geometry<T>>
    // little endian
    result.write_u8(1);
        match geom {
        &Geometry::Point(p) => {
            result.write_u32::<LittleEndian>(1);
            write_point(&p.0, &mut result);
        },
        &Geometry::LineString(ref ls) => {
            result.write_u32::<LittleEndian>(2);
            write_many_points(&ls.0, &mut result);
        },
        &Geometry::Line(ref l) => {
            result.write_u32::<LittleEndian>(2);
            write_many_points(&[l.start, l.end], &mut result);
        },
        &Geometry::Polygon(ref p) => {
            result.write_u32::<LittleEndian>(3);
            result.write_u32::<LittleEndian>(1 + p.interiors().len() as u32);
            write_many_points(&p.exterior().0, &mut result);
            for i in p.interiors().iter() {
                write_many_points(&i.0, &mut result);
            }
        }
        &Geometry::MultiPoint(ref mp) => {
            result.write_u32::<LittleEndian>(4);
            write_many_points(&mp.0.iter().map(|p| p.0).collect::<Vec<Coordinate<T>>>(), &mut result);
        },
        &Geometry::MultiLineString(ref mls) => {
            result.write_u32::<LittleEndian>(5);
            result.write_u32::<LittleEndian>(mls.0.len() as u32);
            for ls in mls.0.iter() {
                // I tried to have this call write_geom_to_wkb again, but I couldn't get the types
                // working.
                result.write_u8(1);
                result.write_u32::<LittleEndian>(2);
                write_many_points(&ls.0, &mut result);
            }
        },
        &Geometry::MultiPolygon(ref mp) => {
            result.write_u32::<LittleEndian>(6);
            result.write_u32::<LittleEndian>(mp.0.len() as u32);
            for poly in mp.0.iter() {
                result.write_u8(1);
                result.write_u32::<LittleEndian>(3);
                result.write_u32::<LittleEndian>(1 + poly.interiors().len() as u32);

                write_many_points(&poly.exterior().0, &mut result);
                for int in poly.interiors().iter() {
                    write_many_points(&int.0, &mut result);
                }
            }
        },
        &Geometry::GeometryCollection(ref gc) => {
            result.write_u32::<LittleEndian>(7);
            result.write_u32::<LittleEndian>(gc.len() as u32);
            for geom in gc.0.iter() {
                write_geom_to_wkb(geom, result)
            }
        }
    }

}

/// Read a Geometry from a reader. Converts WKB to a Geometry.
pub fn wkb_to_geom<I: Read>(mut wkb: &mut I) -> Result<Geometry<f64>, WKBReadError> {
    match wkb.read_u8()? {
        0 => unimplemented!(),
        1 => { },  // LittleEndian, OK
        _ => panic!(),
    };

    match wkb.read_u32::<LittleEndian>()? {
        1 => {
            // Point
            Ok(Geometry::Point(Point(read_point(&mut wkb)?)))
        },
        2 => {
            // LineString
            let points = read_many_points(&mut wkb)?;
            Ok(Geometry::LineString(LineString(points)))
        },
        3 => {
            // Polygon
            let num_rings = wkb.read_u32::<LittleEndian>()? as usize;
            let exterior = read_many_points(&mut wkb)?;
            let mut interiors = Vec::with_capacity(num_rings-1);
            for _ in 0..(num_rings-1) {
                interiors.push(LineString(read_many_points(&mut wkb)?));
            }
            Ok(Geometry::Polygon(Polygon::new(LineString(exterior), interiors)))
        },
        4 => {
            // MultiPoint
            let points = read_many_points(&mut wkb)?;
            Ok(Geometry::MultiPoint(MultiPoint(points.into_iter().map(Point).collect::<Vec<Point<f64>>>())))
        },
        5 => {
            // MultiLineString
            let num_linestrings = wkb.read_u32::<LittleEndian>()? as usize;
            let mut linestrings = Vec::with_capacity(num_linestrings);
            for _ in 0..num_linestrings {
                let linestring: LineString<f64> = match wkb_to_geom(wkb)? {
                    Geometry::LineString(l) => l,
                    _ => { return Err(WKBReadError::WrongType); },
                };

                linestrings.push(linestring);
            }
            Ok(Geometry::MultiLineString(MultiLineString(linestrings)))
        },
        6 => {
            // MultiPolygon
            let num_polygons = wkb.read_u32::<LittleEndian>()? as usize;
            let mut polygons = Vec::with_capacity(num_polygons);
            for _ in 0..num_polygons {
                let polygon: Polygon<f64> = match wkb_to_geom(wkb)? {
                    Geometry::Polygon(p) => p,
                    _ => { return Err(WKBReadError::WrongType); },
                };

                polygons.push(polygon);
            }

            Ok(Geometry::MultiPolygon(MultiPolygon(polygons)))
        },
        _ => unimplemented!(),
    }

}


#[cfg(test)]
mod tests {
    use super::*;

    fn assert_two_f64<R: Read, I: Into<f64>>(reader: &mut R, a: I, b: I) {
        assert_eq!(reader.read_f64::<LittleEndian>().unwrap(), a.into());
        assert_eq!(reader.read_f64::<LittleEndian>().unwrap(), b.into());
    }

    fn write_two_f64<W: Write, F: Into<f64>>(writer: &mut W, a: F, b: F) {
        writer.write_f64::<LittleEndian>(a.into());
        writer.write_f64::<LittleEndian>(b.into());
    }

    #[test]
    fn point_to_wkb() {
        let p: Geometry<f64> = Geometry::Point(Point::new(2., 4.));
        let res = geom_to_wkb(&p);
        let mut res = res.as_slice();
        assert_eq!(res.read_u8().unwrap(), 1);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 1);
        assert_two_f64(&mut res, 2, 4);

        assert_eq!(wkb_to_geom(&mut geom_to_wkb(&p).as_slice()).unwrap(), p);
    }

    #[test]
    fn wkb_to_point() {
        let mut bytes = Vec::new();
        bytes.write_u8(1);
        bytes.write_u32::<LittleEndian>(1);
        bytes.write_f64::<LittleEndian>(100.);
        bytes.write_f64::<LittleEndian>(-2.);

        let geom = wkb_to_geom(&mut bytes.as_slice()).unwrap();
        // TODO need a geom.is_point()
        if let Geometry::Point(p) = geom {
            assert_eq!(p.x(), 100.);
            assert_eq!(p.y(), -2.);
        } else {
            assert!(false);
        }

        assert_eq!(geom_to_wkb(&wkb_to_geom(&mut bytes.as_slice()).unwrap()), bytes);
    }

    #[test]
    fn linestring_to_wkb() {
        let ls: LineString<f64> = vec![(0., 0.), (1., 0.), (1., 1.), (0., 1.), (0., 0.)].into();
        let ls = Geometry::LineString(ls);

        let res = geom_to_wkb(&ls);
        let mut res = res.as_slice();
        assert_eq!(res.read_u8().unwrap(), 1);  // LittleEndian
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 2);  // 2 = Linestring
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 5);  // num points

        assert_two_f64(&mut res, 0, 0);
        assert_two_f64(&mut res, 1, 0);
        assert_two_f64(&mut res, 1, 1);
        assert_two_f64(&mut res, 0, 1);
        assert_two_f64(&mut res, 0, 0);

        assert_eq!(wkb_to_geom(&mut geom_to_wkb(&ls).as_slice()).unwrap(), ls);
    }

    #[test]
    fn wkb_to_linestring() {
        let mut bytes = Vec::new();
        bytes.write_u8(1);

        bytes.write_u32::<LittleEndian>(2);
        bytes.write_u32::<LittleEndian>(2);

        write_two_f64(&mut bytes, 0, 0);
        write_two_f64(&mut bytes, 1000, 1000);

        let geom = wkb_to_geom(&mut bytes.as_slice()).unwrap();
        if let Geometry::LineString(ls) = geom {
            assert_eq!(ls.0.len(), 2);
            assert_eq!(ls.0[0].x, 0.);
            assert_eq!(ls.0[0].y, 0.);
            assert_eq!(ls.0[1].x, 1000.);
            assert_eq!(ls.0[1].y, 1000.);
        } else {
            assert!(false);
        }

        assert_eq!(geom_to_wkb(&wkb_to_geom(&mut bytes.as_slice()).unwrap()), bytes);
    }


    #[test]
    fn polygon_to_wkb() {
        let ls = vec![(0., 0.), (10., 0.), (10., 10.), (0., 10.), (0., 0.)].into();
        let int = vec![(2., 2.), (2., 4.), (4., 4.), (4., 2.), (2., 2.)].into();
        let p = Geometry::Polygon(Polygon::new(ls, vec![int]));

        let res = geom_to_wkb(&p);
        let mut res = res.as_slice();
        assert_eq!(res.read_u8().unwrap(), 1);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 3);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 2);

        // Exterior Ring
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 5);

        assert_two_f64(&mut res, 0, 0);
        assert_two_f64(&mut res, 10, 0);
        assert_two_f64(&mut res, 10, 10);
        assert_two_f64(&mut res, 0, 10);
        assert_two_f64(&mut res, 0, 0);

        // interior ring
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 5);

        assert_two_f64(&mut res, 2, 2);
        assert_two_f64(&mut res, 2, 4);
        assert_two_f64(&mut res, 4, 4);
        assert_two_f64(&mut res, 4, 2);
        assert_two_f64(&mut res, 2, 2);

        assert_eq!(wkb_to_geom(&mut geom_to_wkb(&p).as_slice()).unwrap(), p);
    }

    #[test]
    fn wkb_to_polygon() {
        let mut bytes = Vec::new();
        bytes.write_u8(1);
        bytes.write_u32::<LittleEndian>(3);
        bytes.write_u32::<LittleEndian>(1);
        bytes.write_u32::<LittleEndian>(4);

        write_two_f64(&mut bytes, 0, 0);
        write_two_f64(&mut bytes, 1, 0);
        write_two_f64(&mut bytes, 0, 1);
        // WKB requires that polygons are closed
        write_two_f64(&mut bytes, 0, 0);

        let geom = wkb_to_geom(&mut bytes.as_slice()).unwrap();
        if let Geometry::Polygon(p) = geom {
            assert_eq!(p.interiors().len(), 0);
            assert_eq!(p.exterior().0.len(), 4);
            assert_eq!(p.exterior().0[0], (0., 0.).into());
            assert_eq!(p.exterior().0[1], (1., 0.).into());
            assert_eq!(p.exterior().0[2], (0., 1.).into());
            assert_eq!(p.exterior().0[3], (0., 0.).into());
        } else {
            assert!(false);
        }

        assert_eq!(geom_to_wkb(&wkb_to_geom(&mut bytes.as_slice()).unwrap()), bytes);
    }

    #[test]
    fn wkb_to_polygon_auto_closed() {
        let mut bytes = Vec::new();
        bytes.write_u8(1);
        bytes.write_u32::<LittleEndian>(3);
        bytes.write_u32::<LittleEndian>(1);

        // only 3 points
        bytes.write_u32::<LittleEndian>(3);

        write_two_f64(&mut bytes, 0, 0);
        write_two_f64(&mut bytes, 1, 0);
        write_two_f64(&mut bytes, 0, 1);

        // We /should/ add this
        //write_two_f64(&mut bytes, 0, 0);

        let geom = wkb_to_geom(&mut bytes.as_slice()).unwrap();
        if let Geometry::Polygon(p) = geom {
            assert_eq!(p.interiors().len(), 0);
            assert_eq!(p.exterior().0[0], (0., 0.).into());
            assert_eq!(p.exterior().0[1], (1., 0.).into());
            assert_eq!(p.exterior().0[2], (0., 1.).into());

            // And yet, the geo-types library has add this point
            assert_eq!(p.exterior().0[3], (0., 0.).into());
            assert_eq!(p.exterior().0.len(), 4);
        } else {
            assert!(false);
        }

        // They won't equal
        assert_ne!(geom_to_wkb(&wkb_to_geom(&mut bytes.as_slice()).unwrap()), bytes);
    }


    #[test]
    fn multipoint_to_wkb() {
        let p: Geometry<f64> = Geometry::MultiPoint(MultiPoint(vec![Point::new(0., 0.), Point::new(10., -2.)]));
        let res = geom_to_wkb(&p);
        let mut res = res.as_slice();
        assert_eq!(res.read_u8().unwrap(), 1);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 4);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 2);
        assert_two_f64(&mut res, 0, 0);
        assert_two_f64(&mut res, 10, -2);

        assert_eq!(wkb_to_geom(&mut geom_to_wkb(&p).as_slice()).unwrap(), p);
    }

    #[test]
    fn wkb_to_multipoint() {
        let mut bytes = Vec::new();
        bytes.write_u8(1);
        bytes.write_u32::<LittleEndian>(4);
        bytes.write_u32::<LittleEndian>(1);
        write_two_f64(&mut bytes, 100, -2);

        let geom = wkb_to_geom(&mut bytes.as_slice()).unwrap();
        if let Geometry::MultiPoint(mp) = geom {
            assert_eq!(mp.0.len(), 1);
            assert_eq!(mp.0[0].x(), 100.);
            assert_eq!(mp.0[0].y(), -2.);
        } else {
            assert!(false);
        }

        assert_eq!(geom_to_wkb(&wkb_to_geom(&mut bytes.as_slice()).unwrap()), bytes);
    }

    #[test]
    fn multilinestring_to_wkb() {
        let ls = Geometry::MultiLineString(MultiLineString(vec![
                    vec![(0., 0.), (1., 1.)].into(),
                    vec![(10., 10.), (10., 11.)].into(),
                   ]));

        let res = geom_to_wkb(&ls);
        let mut res = res.as_slice();
        assert_eq!(res.read_u8().unwrap(), 1);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 5); // 5 - MultiLineString
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 2); // 2 linestrings

        assert_eq!(res.read_u8().unwrap(), 1);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 2);  // 2 = Linestring
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 2);  // num points
        assert_two_f64(&mut res, 0, 0);
        assert_two_f64(&mut res, 1, 1);

        assert_eq!(res.read_u8().unwrap(), 1);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 2);  // 2 = Linestring
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 2);  // num points
        assert_two_f64(&mut res, 10, 10);
        assert_two_f64(&mut res, 10, 11);

        assert_eq!(wkb_to_geom(&mut geom_to_wkb(&ls).as_slice()).unwrap(), ls);
    }

    #[test]
    fn wkb_to_multilinestring() {
        let mut bytes = Vec::new();
        bytes.write_u8(1);
        bytes.write_u32::<LittleEndian>(5);
        bytes.write_u32::<LittleEndian>(1);

        bytes.write_u8(1);
        bytes.write_u32::<LittleEndian>(2);
        bytes.write_u32::<LittleEndian>(3);
        write_two_f64(&mut bytes, 0, 0);
        write_two_f64(&mut bytes, 1, 0);
        write_two_f64(&mut bytes, 0, 1);

        let geom = wkb_to_geom(&mut bytes.as_slice()).unwrap();
        if let Geometry::MultiLineString(mls) = geom {
            assert_eq!(mls.0.len(), 1);
            assert_eq!(mls.0[0].0.len(), 3);
            assert_eq!(mls.0[0].0[0].x_y(), (0., 0.));
            assert_eq!(mls.0[0].0[1].x_y(), (1., 0.));
            assert_eq!(mls.0[0].0[2].x_y(), (0., 1.));
        } else {
            assert!(false);
        }

        assert_eq!(geom_to_wkb(&wkb_to_geom(&mut bytes.as_slice()).unwrap()), bytes);
    }


    #[test]
    fn multipolygon_to_wkb() {
        let ls = vec![(0., 0.), (10., 0.), (10., 10.), (0., 10.), (0., 0.)].into();
        let int = vec![(2., 2.), (2., 4.), (2., 2.)].into();

        let p1 = Polygon::new(ls, vec![]);
        let p2 = Polygon::new(int, vec![]);
        let p = Geometry::MultiPolygon(MultiPolygon(vec![p1, p2]));

        let res = geom_to_wkb(&p);
        let mut res = res.as_slice();
        assert_eq!(res.read_u8().unwrap(), 1);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 6);  // Multipolygon
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 2);  // num polygons

        // polygon 1
        assert_eq!(res.read_u8().unwrap(), 1);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 3);  // polygon
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 1);  // only one ring

        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 5); // 5 points in ring #1
        assert_two_f64(&mut res, 0, 0);
        assert_two_f64(&mut res, 10, 0);
        assert_two_f64(&mut res, 10, 10);
        assert_two_f64(&mut res, 0, 10);
        assert_two_f64(&mut res, 0, 0);

        // polygon 2
        assert_eq!(res.read_u8().unwrap(), 1);
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 3);  // polygon
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 1);  // one ring
        assert_eq!(res.read_u32::<LittleEndian>().unwrap(), 3);  // 3 points in ring #1

        assert_two_f64(&mut res, 2, 2);
        assert_two_f64(&mut res, 2, 4);
        assert_two_f64(&mut res, 2, 2);

        assert_eq!(wkb_to_geom(&mut geom_to_wkb(&p).as_slice()).unwrap(), p);
    }

    #[test]
    fn postgis_wkb_to_multipolygon() {
        let bytes: Vec<u8> = vec![
            0x01, 0x06, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x24, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x24, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x24, 0x40,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x24, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x04,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10,
            0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40,   
        ];

        let geom = wkb_to_geom(&mut bytes.as_slice()).unwrap();

        if let Geometry::MultiPolygon(mp) = geom {
            assert_eq!(mp.0.len(), 2);
            assert_eq!(mp.0[0].exterior().0.len(), 5);
            assert_eq!(mp.0[0].exterior().0[0].x_y(), (0., 0.));
            assert_eq!(mp.0[0].exterior().0[1].x_y(), (10., 0.));
            assert_eq!(mp.0[0].exterior().0[2].x_y(), (10., 10.));
            assert_eq!(mp.0[0].exterior().0[3].x_y(), (0., 10.));
            assert_eq!(mp.0[0].exterior().0[4].x_y(), (0., 0.));

            assert_eq!(mp.0[0].interiors().len(), 0);

            assert_eq!(mp.0[1].exterior().0.len(), 4);
            assert_eq!(mp.0[1].exterior().0[0].x_y(), (2., 2.));
            assert_eq!(mp.0[1].exterior().0[1].x_y(), (2., 4.));
            assert_eq!(mp.0[1].exterior().0[2].x_y(), (4., 2.));
            assert_eq!(mp.0[1].exterior().0[0].x_y(), (2., 2.));
            assert_eq!(mp.0[1].interiors().len(), 0);
        } else {
            assert!(false);
        }

    }

    #[allow(dead_code)]
    fn geometrycollection_to_wkb() {
        // FIXME finish
        let p: Geometry<_> = Point::new(0., 0.).into();
        let l: Geometry<_> = LineString(vec![(10., 0.).into(), (20., 0.).into()]).into();
        let gc: Geometry<_> = Geometry::GeometryCollection(GeometryCollection(vec![p, l]));

        let res = geom_to_wkb(&gc);
        let mut res = res.as_slice();
        assert_eq!(res.read_u8().unwrap(), 1);
    }

    #[test]
    fn test_simple_multilinestring1() {
        let wkb: Vec<u8> = vec![1, 5, 0, 0, 0, 1, 0, 0, 0, 1, 2, 0,
            0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 240, 63, 0, 0, 0, 0, 0, 0, 240, 63];

        let geom = wkb_to_geom(&mut wkb.as_slice()).unwrap();
        assert_eq!(geom, Geometry::MultiLineString(MultiLineString(vec![
              vec![(0., 0.), (1., 1.)].into(),
              ])));
    }

    #[test]
    fn test_simple_multilinestring2() {

        let wkb: Vec<u8> = vec![
            0x01, 0x05, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x00, 0x00,
            0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0x3f,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0x3f, 0x01, 0x02, 0x00, 0x00, 0x00, 0x02,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0x40, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40
        ];

        let geom = wkb_to_geom(&mut wkb.as_slice()).unwrap();
        assert_eq!(geom, Geometry::MultiLineString(MultiLineString(vec![
            vec![(0., 0.), (1., 1.)].into(),
            vec![(2., 2.), (3., 2.)].into(),
        ])));
    }

}
