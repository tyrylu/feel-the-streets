CREATE TABLE "areas" (
        id INTEGER NOT NULL,
        name TEXT NOT NULL,
        state VARCHAR(8) NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME, newest_osm_object_timestamp TEXT,
        PRIMARY KEY (id),
        UNIQUE (name),
        CONSTRAINT areastate CHECK (state IN ('creating', 'getting_changes', 'applying_changes', 'updated'))
);