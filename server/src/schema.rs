table! {
    use diesel::sql_types::{Integer, BigInt, Binary, Text, Timestamp, Nullable};
    use crate::area::AreaStateMapping;
    areas (id) {
                id -> Integer,
        osm_id -> BigInt,
        name -> Text,
        state -> AreaStateMapping,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        newest_osm_object_timestamp -> Nullable<Text>,
        db_size -> BigInt,
        parent_osm_ids -> Nullable<Text>,
        last_update_remark -> Nullable<Text>,
        geometry -> Nullable<Binary>,
    }
}
