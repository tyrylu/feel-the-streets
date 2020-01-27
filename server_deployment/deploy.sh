#!/usr/bin/bash
set -e
mkdir build
cp target/release/{oesc,server,worker,create_area,interpret_area_changes,recreate_all_areas} build/
cp Rocket.toml build/
find . -name '*.yml' -exec cp {} build/ \;
rsync -rvzh -e "ssh -p $DEPLOY_TO_PORT" build/ travis@$DEPLOY_TO:/srv/feel-the-streets/