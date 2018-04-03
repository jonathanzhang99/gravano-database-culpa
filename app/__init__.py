import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
login_manager.login_view = 'login'
bootstrap = Bootstrap()
db = SQLAlchemy()

def create_app(name=__name__):
    app = Flask(name, template_folder='templates')

    db_pass = os.environ.get('DB_PASSWORD')

    app.config.update(
        DEBUG=True,
        SECRET_KEY= os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI = f'postgresql://jz2814:{db_pass}@35.227.79.146/proj1part2',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    bootstrap.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app