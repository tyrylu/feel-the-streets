#!/usr/bin/bash
mkdir build
cp target/release/{server,worker,create_area,interpret_area_changes} build/
find server -name '*.yml' -exec cp {} build/ \;
find server -name '*.toml' -exec cp {} build/ \;
rsync -rvzh -e "ssh -p $DEPLOY_TO_PORT" build/ travis@$DEPLOY_TO:/home/travis/