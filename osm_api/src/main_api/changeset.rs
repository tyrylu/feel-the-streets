use super::raw_changeset::RawChangeset;
use crate::boundary_rect::BoundaryRect;
use std::collections::HashMap;

#[derive(Debug)]
pub enum ChangesetState {
    Open,
    Closed(String),
}

#[derive(Debug)]
pub struct Changeset {
    pub id: u64,
    pub created_at: String,
    pub state: ChangesetState,
    pub user: String,
    pub uid: u64,
    pub bounds: Option<BoundaryRect>,
    pub changes_count: u32,
    pub comments_count: u32,
    pub tags: HashMap<String, String>,
}

impl From<RawChangeset> for Changeset {
    fn from(raw: RawChangeset) -> Self {
        let bounds = if let (Some(min_x), Some(min_y), Some(max_x), Some(max_y)) =
            (raw.min_lon, raw.min_lat, raw.max_lon, raw.max_lat)
        {
            Some(BoundaryRect {
                min_x,
                min_y,
                max_x,
                max_y,
            })
        } else {
            None
        };
        let state = if raw.is_open {
            ChangesetState::Open
        } else {
            ChangesetState::Closed(raw.closed_at.unwrap())
        };
        let mut tags = HashMap::with_capacity(raw.tags.len());
        for tag in raw.tags {
            tags.insert(tag.k.into(), tag.v.into());
        }
        Self {
            state,
            bounds,
            tags,
            id: raw.id,
            created_at: raw.created_at,
            uid: raw.uid,
            user: raw.user,
            changes_count: raw.changes_count,
            comments_count: raw.comments_count,
        }
    }
}
