import os

from flask import Flask
from flask_migrate import Migrate

from extension import db
from auth.controller import auth

config = {
    "stag": "api.config.StagingConfig",
    "test": "api.config.TestConfig",
    "pro": "api.config.ProductionConfig",
    "dev": "api.config.DevelopmentConfig",
}


def create_app(config_mode='dev'):
    app = Flask(__name__)
    
    app.config.from_object(config[config_mode])
    db.init_app(app)

    if not app.debug:
        import logging
        logging.basicConfig(level=logging.INFO)
        from logging import FileHandler
        file_handler = FileHandler(app.config['LOG_FILE'])
        app.logger.addHandler(file_handler)

    app.register_blueprint(auth)
    migrate = Migrate(app, db)
    return app
