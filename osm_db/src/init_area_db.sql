SELECT InitSpatialMetadata(1, 'WGS84');
CREATE TABLE entities (
	id VARCHAR(16) PRIMARY KEY,
	discriminator VARCHAR(64) NOT NULL,
	data TEXT NOT NULL,
	effective_width FLOAT);
SELECT AddGeometryColumn("entities", "geometry", 4326, "GEOMETRY", 2, 1);
SELECT CreateSpatialIndex('entities', 'geometry');
CREATE INDEX idx_entity_by_name on entities(json_extract(data, "$.name"));
CREATE INDEX idx_entity_by_name_lower on entities(lower(json_extract(data, "$.name")));
CREATE TABLE entity_relationships (parent_id VARCHAR(16) REFERENCES entities(id) ON DELETE CASCADE, child_id VARCHAR(16) REFERENCES entities(id) ON DELETE CASCADE, kind INTEGER CHECK (KIND in (0, 1, 2)), PRIMARY KEY (parent_id, child_id, kind));