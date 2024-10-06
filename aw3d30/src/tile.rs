use crate::dataset_naming;
use crate::error::Error;
use crate::Result;
use std::io::Cursor;
use std::fs::File;
use std::ops::RangeInclusive;
use std::path::Path;
use tiff::decoder::{Decoder, DecodingResult};

pub(crate) struct Tile {
    data: Vec<i16>,
}

impl Tile {
    pub(crate) fn for_coords(lat: f64, lon: f64, storage_root: &Path) -> Result<Self> {
        let tile_id = dataset_naming::tile_id_for(lat, lon);
        let tile_path = storage_root.join(tile_id).with_extension("ztif");
        let file = File::open(tile_path)?;
        let decompressed = zstd::decode_all(file)?;
        let mut decoder = Decoder::new(Cursor::new(decompressed))?;
        let data = decoder.read_image()?;
        if let DecodingResult::I16(data) = data {
            Ok(Self { data })
        } else {
            Err(Error::UnexpectedPixelFormat)
        }
    }

    pub(crate) fn data_for_row_part(&mut self, row: u16, col_range: RangeInclusive<u16>) -> Result<Vec<i16>> {
        let whole_rows_offset = (row * 3600) as usize;
        Ok(self.data[whole_rows_offset + *col_range.start() as usize..=whole_rows_offset + *col_range.end() as usize].to_vec())
    }
}
