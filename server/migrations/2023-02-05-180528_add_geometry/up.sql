select load_extension("mod_spatialite");
select initSpatialMetadata(1);
select addGeometryColumn("areas", "geometry", 4326, "GEOMETRY", 2);