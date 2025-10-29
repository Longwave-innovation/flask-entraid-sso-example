from flask import Flask
from config import Config
from app.logger import setup_logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    setup_logging(app)
    
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app