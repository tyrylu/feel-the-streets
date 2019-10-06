BEGIN;
CREATE TABLE "new_areas" (
        id INTEGER NOT NULL,
        name TEXT NOT NULL,
        state VARCHAR(8) NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME, newest_osm_object_timestamp TEXT,
        PRIMARY KEY (id),
        UNIQUE (name),
        CONSTRAINT areastate CHECK (state IN ('creating', 'getting_changes', 'applying_changes', 'updated'))
);
INSERT INTO new_areas SELECT id, name, state, created_at, updated_at, newest_osm_object_timestamp FROM areas;
DROP TABLE areas;
ALTER TABLE new_areas RENAME TO areas;
COMMIT;