import os

from flask import Flask
from flask_migrate import Migrate

from extension import db


def create_app(config_mode='dev'):
    app = Flask(__name__)

    config = ''    
    if config_mode == 'stag':
        config = 'api.config.StagingConfig'
    elif config_mode == 'pro':
        config = 'api.config.ProductionConfig'
    elif config_mode == 'test':
        config = 'api.config.TestConfig'
    else:
        config = 'api.config.DevelopmentConfig'
    
    app.config.from_object(config)
    db.init_app(app)

    if not app.debug:
        import logging
        logging.basicConfig(level=logging.INFO)
        from logging import FileHandler
        file_handler = FileHandler(app.config['LOG_FILE'])
        app.logger.addHandler(file_handler)

    migrate = Migrate(app, db)
    return app
    