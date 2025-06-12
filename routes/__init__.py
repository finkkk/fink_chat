# routes/__init__.py
from flask import Blueprint  # noqa: F401

from .auth import auth_bp
from .system import system_bp
from .view import view_bp
from .seo import seo_bp
from .polls import polls_bp

def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(view_bp)
    app.register_blueprint(seo_bp)
    app.register_blueprint(polls_bp)