import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import dotenv
from .config import Config
from .amqp_huey import AMQPHuey

app = Flask(__name__)
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
huey = AMQPHuey(broker_url=app.config["AMQP_BROKER_URL"], consume=bool(os.environ.get("CONSUME", "False")))
from . import models, routes
