# Feel the streets

This project aims to create something like Google Street view, but for visually impaired users.
There already are some applications which can present the world's map on the level of city/village positions, but nothing what i was able to determine yet presents it on the individual area detail.

## Requirements
### Client

This application requires Python 3.6 to work, because it utilizes the new variable annotation syntax.
For the rest of the requirements see app_requirements.txt.
The majority of them can be installed by invoking a pip install -r app_requirements.txt without much trouble.
You can simplify PySide2 installation by using your distribution's prebuild package, for example, python3-PySide2 in Fedora.
You can do something similar with shapely, e. g. python3-shapely package is a good idea to have, because there appear not to be any binary wheels for Linux for these two.

In addition to the python requirements, it requires the loadable spatialite sqlite3 extension and under Linux, you need to install the openal library manually as well. In fedora, those are the libspatialite and openal packages.
Optionally, it can use the sqlite3 icu loadable extension. The resulting .so/.dll should be named icu.so or icu.dll, so the sqlite3 extension loading will find the entry point.
### Rust components
The Rust components handle dependencies as any Rust project, so a cargo build in the root should do the trick. A release build should be performed in production, however.
Note that because of Rocket a nightly rust compiler is necessary, see the Rustup installation instructions and choose nightly during the initial Rustup install, or, if you already have Rustup installed, rustup toolchain add nightly should suffice to get one, then you either set is as a default or add a per project override (see the Rustup docs for the details).
In addition, it requires the development files for Openssl.
## Components

The basic components in the repository are:
- app - the desktop application
- oesc - the online schema maitenance tool
- server - the api server which the desktop app uses to download and check available maps, also some server related management commands for schema changes.

They might be split in the future, however.

## Running the server

The server expects a Rabbitmq server running. The credentials should be in a file named .env, which should be placed in the project root directory. It should look something like the following:
AMQP_BROKER_URL="amqp://user:password@rabbitmq_host/%2f"
Note that the used Rabbitmq user needs privileges to declare queues and exchanges, along with the needed bindings. In addition to the plaintext amqp protocol, you can use TLS encryption if you specify amqps in the protocol in the URI.
To run it, after cargo build, just run target/debug/server.

## Running the client
If you want to use the default server, just run run_app.py with a Python interpreter. If you want to use a different server, you can set the API_ENDPOINT environment variable to the URL of the server, e. g. http://localhost:5000 or similar. Don't forget the path, if the server endpoints are under one.
Also, if you're doing this, AMQP_BROKER_URL environment variable should be set to the URL of the AMQP broker, see the example in the server execution section for an example. Note that in this case, no .env file is being loaded and the environment variables must be real ones.