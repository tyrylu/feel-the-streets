#!/usr/bin/bash
set -e
mkdir to_deploy
if [ "$TRAVIS_OS_NAME" = "windows" ]
then
cp target/release/*.exe to_deploy/
cd dist/fts
7z a ../../to_deploy/fts.zip .
cd ../..
else
cp target/release/{oesc,server,worker,create_area,recreate_all_areas,libosm_db\.so} to_deploy/
fi
cp Rocket.toml to_deploy/
find . -name '*.yml' -exec cp {} to_deploy/ \;
rsync -zzrvh -e "ssh -o StrictHostKeyChecking=no -p $DEPLOY_TO_PORT" to_deploy/ travis@$DEPLOY_TO:/srv/feel-the-streets/