Feel the streets
================
This project aims to create something like Google Street view, but for visually impaired users.
There already are some applications which can present the world's map on the level of city/village positions, but nothing what i was able to determine yet presents it on the individual area detail.

Requirements
------------
This application requires Python 3.6 to work, because it utilizes the new variable annotation syntax.
For the rest of the requirements see the requirement files.
The majority of them can be installed by invoking a pip install -r requirements/app.txt for the desktop app, or pip install -r requirements/server.txt for the server component.
Using a shared pipfile would be nice, but until pipfile supports more than the dev packages directive, it is not possible.

Components
----------
The basic components in the repository are:
- app - the desktop application
- fts_tool - command line utilities, mainly for development, currently broken
- server - the api server which the desktop app uses to download and check available maps

They might be split in the future, however.

Running the server
------------------
Not including the python package requirements, the server requires a running Rabbitmq broker with the delayed messages extension installed.
The requirement for the extension might be relaxed in the future, but it is not a high priority task, but if someone wants, he can submit a pull request which makes it at least optional. It is doable, but i am afraid that the scheduling code will not be as efficient.
If you want to run the flask development server, first set the FLASK_APP environment variable. Assuming you are in the project root, its value would be server.
Next, you just run flask run.