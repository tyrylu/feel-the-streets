BEGIN;
CREATE TABLE "new_areas" (
        id INTEGER NOT NULL,
        name TEXT NOT NULL,
        state VARCHAR(8) NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME, newest_osm_object_timestamp TEXT, osm_id INTEGER NOT NULL DEFAULT 0, db_size INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (id),
        UNIQUE (name),
        CONSTRAINT areastate CHECK (state IN ('creating', 'getting_changes', 'applying_changes', 'updated', 'frozen'))
);
INSERT INTO new_areas SELECT * from AREAS;
DROP TABLE areas;
ALTER TABLE new_areas RENAME TO areas;
COMMIT;