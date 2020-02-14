# Feel the streets

This project aims to create something like Google Street view, but for visually impaired users.
There already are some applications which can present the world's map on the level of city/village positions, but nothing what i was able to determine yet presents it on the individual area detail.

## Requirements

This application requires Python 3.6 to work, because it utilizes the new variable annotation syntax.
For the rest of the requirements see the requirement files.
The majority of them can be installed by invoking a pip install -r app_requirements.txt
You can simplify PySide2 installation by using your distribution's prebuild package, for example, python3-PySide2 in Fedora.
You can do something similar with shapely, e. g. python3-shapely package is a good idea to have.

In addition to the python requirements, it requires the loadable spatialite sqlite3 extension and under Linux, you need to install the openal library manually as well. In fedora, those are the libspatialite and openal packages.
Optionally, it can use the sqlite3 icu loadable extension. The resulting .so/.dll should be named icu.so or icu.dll, so the sqlite3 extension loading will find the entry point.
The Rust components handle dependencies as any Rust project, so a cargo build in the root should do the trick.
Note that because of Rocket a nightly rust compiler is necessary.
And also the development headers for Openssl 
## Components

The basic components in the repository are:
- app - the desktop application
- oesc - the online schema maitenance tool
- server - the api server which the desktop app uses to download and check available maps, also some server related management commands for schema changes.

They might be split in the future, however.

## Running the server

The server expects a Rabbitmq server running. The credentials should be in an environment variable named AMQP_BROKER_UR or in a .env file.
To run it, after cargo build, just run target/debug/server.