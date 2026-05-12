from flask import Flask, redirect, url_for
from flask_login import current_user
from config import config
from app.extensions import db, login_manager

def create_app(config_name: str = "default") -> Flask:
    """
    App factory. Called once at startup.
    Returns a fully configured Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Bind extensions to this app instance
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints — each is a self-contained section of the app
    from app.blueprints.auth.routes     import auth_bp
    from app.blueprints.expenses.routes import expenses_bp
    from app.blueprints.categories.routes import categories_bp

    app.register_blueprint(auth_bp,       url_prefix="/auth")
    app.register_blueprint(expenses_bp,   url_prefix="/expenses")
    app.register_blueprint(categories_bp, url_prefix="/categories")

    @app.get("/")
    def root():
        if current_user.is_authenticated:
            return redirect(url_for("expenses.index"))
        return redirect(url_for("auth.login"))

    # Create all DB tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
