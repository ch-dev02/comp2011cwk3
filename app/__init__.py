# imports required to function
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging

# configure flask app, database and migrations for database
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

logging.basicConfig(filename='log.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

from app import models
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return models.User.query.get(int(user_id))