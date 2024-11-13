# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Import and register blueprints/routes
    from app.chat_bot import bp
    app.register_blueprint(bp)
    
    return app