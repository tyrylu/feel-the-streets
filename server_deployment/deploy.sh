#!/usr/bin/bash
set -e
mkdir build
cp target/release/{oesc,server,worker,create_area,recreate_all_areas, libosm_db.so} build/
cp Rocket.toml build/
find . -name '*.yml' -exec cp {} build/ \;
rsync -zzrvh -e "ssh -p $DEPLOY_TO_PORT" build/ travis@$DEPLOY_TO:/srv/feel-the-streets/