from flask import Flask
from flask_migrate import Migrate

from api.extension import db
from api.auth.controller import auth_blueprint
from api.task.controller import task_blueprint


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

    app.register_blueprint(auth_blueprint, url_prefix='/todolist')
    app.register_blueprint(task_blueprint, url_prefix='/todolist')
    migrate = Migrate(app, db)
    return app
