#!/usr/bin/bash
mkdir build
cp target/release/{server,worker,create_area,interpret_area_changes} build/
cp server/Rocket.toml build/
find server -name '*.yml' -exec cp {} build/ \;
mkdir build/debug
cp target/debug/{server,worker,create_area,interpret_area_changes} build/debug/
rsync -rvzh -e "ssh -p $DEPLOY_TO_PORT" build/ travis@$DEPLOY_TO:/srv/feel-the-streets/