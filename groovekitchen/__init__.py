from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from groovekitchen import config

csrf = CSRFProtect()

def create_app():
    from groovekitchen.models import db
    myapp = Flask(__name__, instance_relative_config=True)
    myapp.config.from_pyfile('config.py', silent=True)
    myapp.config.from_object(config.DevelopmentConfig)
    db.init_app(myapp)
    csrf.init_app(myapp)
    migrate = Migrate(myapp, db)
    return myapp


app = create_app()
from groovekitchen import customer_route, routes, agent_route, chef_route, caterer_route, admin_route
