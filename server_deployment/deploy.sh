#!/usr/bin/bash
mkdir build
find target/release -type f -executable -exec cp {} build/ \;
find server -name '*.yml' -exec cp {} build/ \;
rsync -rvzh -e "ssh -p $DEPLOY_TO_PORT" build/ travis@$DEPLOY_TO:/home/travis/