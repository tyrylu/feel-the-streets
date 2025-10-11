use crate::coordinate_ops::{get_pixel_ranges, ranges_length, RangeInfo};
use crate::dataset_naming::{tile_id_for, tile_id_from_archive_filename, tileset_url};
use crate::elevation_map::ElevationMap;
use crate::tile::Tile;
use crate::Result;
use log::{debug, info};
use std::io::{Cursor, Read};
use std::path::PathBuf;

pub struct Dataset {
    storage_root: PathBuf,
}

impl Dataset {
    pub fn new(storage_root: impl Into<PathBuf>) -> Self {
        Self {
            storage_root: storage_root.into(),
        }
    }

    fn ensure_has_tile_for(&self, latitude: f64, longitude: f64) -> Result<()> {
        let tile_id = tile_id_for(latitude, longitude);
        let tileset_url = tileset_url(latitude, longitude);
        let tile_path = self.storage_root.join(&tile_id).with_extension("ztif");
        if !tile_path.exists() {
            std::fs::create_dir_all(&self.storage_root)?;
            let tileset_resp = ureq::get(&tileset_url).call()?;
            let content_length = tileset_resp.body().content_length().unwrap();
            info!("Received request for tile {} which was missing from local storage, downloading containing tileset of size {} bytes.", tile_id, content_length);
            let mut data = Vec::with_capacity(content_length as usize);
            tileset_resp
                .into_body()
                .into_reader()
                .read_to_end(&mut data)?;
            info!("Download completed, caching tileset.");
            let mut zip = zip::ZipArchive::new(Cursor::new(data))?;
            for name in 0..zip.len() {
                let mut file = zip.by_index(name)?;
                if !file.name().ends_with("DSM.tif") {
                    continue;
                }
                let file_path = self
                    .storage_root
                    .join(tile_id_from_archive_filename(file.name())?)
                    .with_extension("ztif");
                debug!("Extracting {} to {}", file.name(), file_path.display());
                let mut dest = std::fs::File::create(&file_path)?;
                zstd::stream::copy_encode(&mut file, &mut dest, 22)?;
            }
            info!("Tileset processed.");
        }
        Ok(())
    }

    fn tile_for(&self, lat: f64, lon: f64) -> Result<Tile> {
        self.ensure_has_tile_for(lat, lon)?;
        Tile::for_coords(lat, lon, self.storage_root.as_path())
    }

    pub fn create_elevation_map_for_area(
        &self,
        min_lat: f64,
        min_lon: f64,
        max_lat: f64,
        max_lon: f64,
    ) -> Result<ElevationMap> {
        let x_ranges = get_pixel_ranges(min_lon, max_lon);
        let y_ranges = get_pixel_ranges(min_lat, max_lat); // Latitude is decreasing in the tiles, so should in our elevation map as well, but we'll compensate for it when going through them.
        let mut result = vec![];
        for y_range in y_ranges.iter().rev() {
            result.extend(self.create_elevation_map_block(x_ranges.as_ref(), y_range)?);
        }

        Ok(ElevationMap {
            origin_lat: max_lat,
            origin_lon: min_lon,
            width: ranges_length(&x_ranges),
            height: ranges_length(&y_ranges),
            data: result,
        })
    }

    fn create_elevation_map_block(
        &self,
        x_ranges: &[RangeInfo],
        y_range: &RangeInfo,
    ) -> Result<Vec<i16>> {
        let mut result = vec![];
        let mut tiles = vec![];
        for x_range in x_ranges {
            tiles.push(self.tile_for(y_range.tile_bound.abs(), x_range.tile_bound)?);
        }
        for y_coord in y_range.range.clone().rev() {
            for (i, tile) in tiles.iter_mut().enumerate() {
                result.extend(tile.data_for_row_part(3599 - y_coord, x_ranges[i].range.clone())?);
            }
        }
        Ok(result)
    }
}
