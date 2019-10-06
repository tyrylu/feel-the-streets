table! {
    use diesel::sql_types::{Integer, BigInt, Text, Timestamp, Nullable};
    use crate::area::AreaStateMapping;
    areas (id) {
                id -> Integer,
        osm_id -> BigInt,
        name -> Text,
        state -> AreaStateMapping,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        newest_osm_object_timestamp -> Nullable<Text>,
    }
}
