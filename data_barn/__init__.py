from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import uuid

app = Flask(__name__, instance_relative_config=True)

app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.login_view = "auth.user_login"
login_manager.init_app(app)

from .models import User

@login_manager.user_loader
def load_user(user_id):
  try:
    return User.query.get(uuid.UUID(user_id))
  except:
    return None

from . import models, user_auth

app.register_blueprint(user_auth.bp)

from . import dashboard

app.register_blueprint(dashboard.bp)
app.add_url_rule("/", endpoint="dashboard")
#from app import models

#with app.app_context():
#  db.create_all()

#@app.route('/')
#def hello():
#  return {"hello": "world"}


if __name__ == "__main__":
  app.run(debug=True)
