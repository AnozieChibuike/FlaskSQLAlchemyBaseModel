# app.py
from flask import Flask
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flasksqlalchemybasemodel import db, BaseModel


base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, "database", "test.db")


# config.py
class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    

def create_app():
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    db.init_app(app)
    return app
