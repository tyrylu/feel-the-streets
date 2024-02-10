# Feel the streets

This project aims to create something like Google Street view, but for visually impaired users.
There already are some applications which can present the world's map on the level of city/village positions, but nothing what i was able to determine yet presents it on the individual area detail.

## Requirements
### Client

This application requires Python 3.6 to work, because it utilizes the new variable annotation syntax.
For the rest of the requirements see app_requirements.txt.
The majority of them can be installed by invoking a pip install -r app_requirements.txt without much trouble.
You can simplify PySide2 installation by using your distribution's prebuild package, for example, python3-PySide2 in Fedora.

In addition to the python requirements, it requires the loadable spatialite sqlite3 extension and under Linux, you need to install the openal library manually as well. In fedora, those are the libspatialite and openal packages.
Optionally, it can use the sqlite3 icu loadable extension. The resulting .so/.dll should be named icu.so or icu.dll, so the sqlite3 extension loading will find the entry point.

Also, the Python application requires the osm_db_py rust library somewhere in the Python's search path.
There are basically two ways how to do that:
* Copy the libosm_db.so file from the target/debug or target/release directories to the project root directory as osm_db.so, e. g. you drop the lib prefix. Somewhat hackish, but it works.
* You build a proper wheel using Maturin - the steps are as follows:
  * Install it: pip install maturin
  * Change to the osm_db_py directory
  * Run maturin build --release --manylinux 1-unchecked
  * Install the resulting wheel: pip install ../target/wheels/*.whl
### Rust components
The Rust components handle dependencies as any Rust project, so a cargo build in the root should do the trick. A release build should be performed in a production environment, however.
Because of the Clap dependency, you need at least Rust 1.74. You can use a distribution package, if it is new enough, or you can use rustup to install a recent stable version.
In addition, it requires the development files for Openssl.

## Components

The basic components in the repository are:
- app - the desktop application
- oesc - the online schema maitenance tool
- server - the API server which the desktop app uses to download and check available maps, also some server-related management commands for schema changes.

They might be split in the future, however.

## Running the server

The server expects a Redis server running. The credentials should be in a file named .env, which should be placed in the project root directory. It should look something like the following:
REDIS_URL="redis://user:password@redis_host"
Note that the used Redis user needs privileges to modify ACLs for application users, so it is basically an admin. In addition to the plaintext Redis protocol, you can use TLS encryption if you specify rediss in the protocol in the URI. It is also possible to use an unix socket using the redis+unix or unix protocols in the connection URL, these two protocols are interchangeable.
To run it, after the usual cargo build, just run target/debug/server.

## Runtime client requirements
- The application is accessing the network for area downloads at the following DNS names: mail.trycht.cz
- The network access is needed for the first time, afterward, the access is not required, and the currently downloaded copies will be used
### Windows
- The application was tested on Windows 10 64-bit
- It is assumed that the user has a speech synthesizer of the correct language installed
- The speech subsystem first tries to use a running screen reader (NVDA, JAWS or Window-Eyes), then it falls back to SAPI 5
- To set the used voice, if a screen reader is used, see the specific screen reader configuration
- If using Sapi 5, the configuration is reachable by opening the Run dialog and executing the following file: C:\Windows\System32\Speech\SpeechUX\sapi.cpl
### Linux
- The application was tested on Fedora 33 64-bit
- The current packaged version requires using A X server, e. g. no Wayland support as of yet
- The application requires a running Speech dispatcher

## Running the client
If you want to use the default server, just run run_app.py with a Python interpreter. If you want to use a different server, you can set the API_ENDPOINT environment variable to the URL of the server, e. g. http://localhost:5000 or similar. Don't forget the path, if the server endpoints are under one.
Also, if you're doing this, the AMQP_BROKER_URL environment variable should be set to the URL of the AMQP broker, see the example in the server execution section for an example. Note that in this case, no .env file is being loaded and the environment variables must be real ones.
## Getting started with the client, e. g. the basic thoughts about it so you don't get completely lost
Because as of now there's no comprehensive documentation, this section of the readme describes the basic concepts of the client application.

### Area selection
After starting up, the area selection dialog is displayed. The list contains all the areas which were requested by previous users and are ready for download.
If you can't find your favorite place, you can request the creation of a new area. If there are multiple matches, e. g. areas with the exact same name, you'll have to select the correct one, the parent's name and the area's tags have to suffice for that.
### The main window
After selecting an area and some download/update operations, the main window is displayed.

The main window is empty except for the menubar at the top, e. g. the area is not represented graphically. At first, you start somewhere near the area's center, so there should be plenty of things around you. You start looking northwest. You can move by pressing the up and down arrow. To look around, the n key should be good enough in the beginning, but note that this command ignores some objects (bus and tram lines for example) for performance reasons.

To know where you are, use the current location command invoked by the l key. If you need some more details, the detailed location command should be of help.
### Moving by bigger distances
Moving by small steps is not always convenient, however. Because of this, you can press enter on an object in the nearby objects dialog and you'll move to it.

You can also search by name using the ctrl+f shortcut, a much more advanced search is available using the advanced search (shortcut ctrl+shift+f).
