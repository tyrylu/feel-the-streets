import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import dotenv
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
from .config import Config
from .amqp_huey import AMQPHuey

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from .huey_creation import get_huey_kwargs
huey = AMQPHuey(**get_huey_kwargs())
from . import models, routes
