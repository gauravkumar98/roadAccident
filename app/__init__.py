from flask import Flask,g
from flask_bcrypt import Bcrypt
from app.config import Config
from app.main.routes import main
from datetime import timedelta

bcrypt = Bcrypt()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.secret_key="secretKeyhggfhjtftfkfkuddvgg"
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
    app.config.from_object(Config)
    bcrypt.init_app(app)
    app.register_blueprint(main)
    return app