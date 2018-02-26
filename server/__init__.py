from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from .amqp_huey import AMQPHuey

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
huey = AMQPHuey(broker_url=app.config["AMQP_BROKER_URL"])
from . import models, routes
