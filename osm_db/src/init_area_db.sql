SELECT InitSpatialMetadata(1);
CREATE TABLE entities (
	id VARCHAR(16) PRIMARY KEY,
	discriminator VARCHAR(64) NOT NULL,
	data TEXT NOT NULL,
	effective_width FLOAT);
SELECT AddGeometryColumn("entities", "geometry", 4326, "GEOMETRY", 2, 1);
SELECT CreateSpatialIndex('entities', 'geometry');
CREATE TABLE entity_relationships (parent_id VARCHAR(16) REFERENCES entities(id) ON DELETE CASCADE, child_id VARCHAR(16) REFERENCES entities(id) ON DELETE CASCADE, PRIMARY KEY (parent_id, child_id));