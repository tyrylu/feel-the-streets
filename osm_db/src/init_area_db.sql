SELECT InitSpatialMetadata(1);
CREATE TABLE entities (
	id INTEGER PRIMARY KEY,
	discriminator VARCHAR(64) NOT NULL,
	data TEXT NOT NULL,
	effective_width FLOAT);
SELECT AddGeometryColumn("entities", "geometry", 4326, "GEOMETRY", 2, 1);
CREATE INDEX entity_by_osm_id on entities(json_extract(data, "$.osm_id"));