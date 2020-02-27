#!/usr/bin/bash
set -e
mkdir build
if [ "$TRAVIS_OS_NAME" = "windows" ]
then
cp target/release/*.exe build/
else
cp target/release/{oesc,server,worker,create_area,recreate_all_areas,libosm_db\.so} build/
fi
cp Rocket.toml build/
find . -name '*.yml' -exec cp {} build/ \;
rsync -zzrvh -e "ssh -o StrictHostKeyChecking=no -p $DEPLOY_TO_PORT" build/ travis@$DEPLOY_TO:/srv/feel-the-streets/