# routes/__init__.py
def init_routes(app):
    from .auth import auth_bp
    from .user import user_bp
    from .chat import chat_bp
    from .generate import generate_bp
    from .history import history_bp
    from .model import model_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(generate_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(model_bp)