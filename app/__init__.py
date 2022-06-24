from flask_login import LoginManager
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import environ
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.debug = True
app.secret_key = environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://" \
                                        f"{environ.get('DB_LOGIN')}:" \
                                        f"{environ.get('DB_PASS')}@" \
                                        f"{environ.get('DB_ADDRESS')}:" \
                                        f"{environ.get('DB_PORT')}/" \
                                        f"{environ.get('DB_NAME')}"
# app.config['SQLALCHEMY_ECHO'] = True

login_manager = LoginManager(app)
# login_manager.login_view = 'auth.login_form'
# login_manager.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))


from app.main import main
from app.auth import auth
from app.user import user
from app.admin import admin
from app.dashboard import dashboard
from app.vacations import vacations

app.register_blueprint(main)
app.register_blueprint(dashboard)
app.register_blueprint(vacations)
app.register_blueprint(auth)
app.register_blueprint(user)
app.register_blueprint(admin)
