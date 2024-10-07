use crate::error::Error;
use crate::Result;

const BASE_DATA_URL: &str = "https://www.eorc.jaxa.jp/ALOS/aw3d30/data/release_v2404";

fn latitude_suffix(latitude: f64) -> char {
    if latitude < 0.0 {
        'S'
    } else {
        'N'
    }
}

fn longitude_suffix(longitude: f64) -> char {
    if longitude < 0.0 {
        'W'
    } else {
        'E'
    }
}

pub(crate) fn tile_id_for(latitude: f64, longitude: f64) -> String {
    let lat_prefix = latitude_suffix(latitude);
    let lon_prefix = longitude_suffix(longitude);
    format!(
        "{}{:03}{}{:03}",
        lat_prefix,
        latitude.ceil().abs(),
        lon_prefix,
        longitude.floor().abs()
    )
}

pub(crate) fn tileset_id_for(latitude: f64, longitude: f64) -> String {
    let lat_origin = (latitude / 5.0).ceil() * 5.0;
    let lon_origin = (longitude / 5.0).floor() * 5.0;
    let lat_bound = lat_origin + 5.0;
    let lon_bound = lon_origin + 5.0;
    let lat_origin_prefix = latitude_suffix(lat_origin);
    let lon_origin_prefix = longitude_suffix(lon_origin);
    let lat_bound_prefix = latitude_suffix(lat_bound);
    let lon_bound_prefix = longitude_suffix(lon_bound);
    format!(
        "{}{:03}{}{:03}_{}{:03}{}{:03}",
        lat_origin_prefix,
        lat_origin.abs(),
        lon_origin_prefix,
        lon_origin.abs(),
        lat_bound_prefix,
        lat_bound.abs(),
        lon_bound_prefix,
        lon_bound.abs()
    )
}

pub(crate) fn tileset_url(latitude: f64, longitude: f64) -> String {
    let tileset_id = tileset_id_for(latitude, longitude);
    format!("{}/{}.zip", BASE_DATA_URL, tileset_id)
}

pub(crate) fn tile_id_from_archive_filename(filename: &str) -> Result<&str> {
    if let Some((_dir, filename)) = filename.split_once('/') {
        if let Some(tile_id) = filename.split('_').nth(1) {
            Ok(tile_id)
        } else {
            Err(Error::InvalidArchiveFilename(filename.to_string()))
        }
    } else {
        Err(Error::InvalidArchiveFilename(filename.to_string()))
    }
}
