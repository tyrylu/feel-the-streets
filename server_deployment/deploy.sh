#!/usr/bin/bash
mkdir build
cp target/release/server build/
rsync -rvzh -e "ssh -p $DEPLOY_TO_PORT" build/ travis@$DEPLOY_TO:/home/travis/