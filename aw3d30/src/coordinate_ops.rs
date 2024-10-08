use std::ops::RangeInclusive;

pub(crate) const DEGREE_PER_PIXEL: f64 = 1.0 / 3600.0;
const MAX_PIXEL: u16 = 3599;

pub(crate) struct RangeInfo {
    pub(crate) tile_bound: f64,
    pub(crate) range: RangeInclusive<u16>,
}

pub(crate) fn get_pixel_ranges(min_coord: f64, max_coord: f64) -> Vec<RangeInfo> {
    let num_tile_changes = (max_coord.floor() - min_coord.floor()) as u16;
    match num_tile_changes {
        0 => vec![
            RangeInfo {
                tile_bound: min_coord.floor(),
                range: coord_to_pixel(min_coord, min_coord.floor())..=coord_to_pixel(max_coord, max_coord.floor()),
            }],
        1 => vec![
            RangeInfo {
                tile_bound: min_coord.floor(),
                range: coord_to_pixel(min_coord, min_coord.floor())..=MAX_PIXEL,
            },
            RangeInfo {
                tile_bound: max_coord.floor(),
                range: 0..=coord_to_pixel(max_coord, max_coord.floor()),
            }],
        _ => {
            let mut ranges = Vec::with_capacity((num_tile_changes + 1).into());
            ranges.push(
                RangeInfo {
                    tile_bound: min_coord.floor(),
                    range: coord_to_pixel(min_coord, min_coord.floor())..=MAX_PIXEL,
        });
            let first_whole_tile = min_coord.floor() as u8 + 1;
            let last_whole_tile = max_coord.floor() as u8 - 1;
            for bound in first_whole_tile..=last_whole_tile {
                ranges.push(
                    RangeInfo {
                        tile_bound: bound as f64,
                        range: 0..=MAX_PIXEL
                    });
                    }
            ranges.push(
                RangeInfo {
                    tile_bound: max_coord.floor(),
                    range: 0..=coord_to_pixel(max_coord, max_coord.floor()),
                });

            ranges
        }
    }
}

pub fn coord_to_pixel(coord: f64, origin: f64) -> u16 {
    ((coord - origin) / DEGREE_PER_PIXEL) as u16
}

pub(crate) fn ranges_length(ranges: &[RangeInfo]) -> u32 {
    ranges.iter().map(|r| (r.range.end() - r.range.start() + 1) as u32).sum()
}