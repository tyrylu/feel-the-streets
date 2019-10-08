Feel the streets
================
This project aims to create something like Google Street view, but for visually impaired users.
There already are some applications which can present the world's map on the level of city/village positions, but nothing what i was able to determine yet presents it on the individual area detail.

Requirements
------------
This application requires Python 3.6 to work, because it utilizes the new variable annotation syntax.
For the rest of the requirements see the requirement files.
The majority of them can be installed by invoking a pip install -r app_requirements.tx.t
In addition to the python requirements, it requires the loadable spatialite sqlite3 extension and the yajl2 library. In Debian, those are the libsqlite3-mod-spatialite and libyajl2 packages.
Optionally, it can use the sqlite3 icu loadable extension. The resulting .so/.dll should be named icu.so or icu.dll, so the sqlite3 extension loading will find the entry point.
The Rust components handle dependencies as any Rust project, so a cargo build in the root should do the trick.

Components
----------
The basic components in the repository are:
- app - the desktop application
- fts_tool - command line utilities, mainly for development, currently broken
- server - the api server which the desktop app uses to download and check available maps

They might be split in the future, however.

Running the server
------------------
The server expects a Rabbitmq server running. The credentials should be in an environment variable named AMQP_BROKER_UR or in a .env file.
To run it, after cargo build, just run target/debug/server.