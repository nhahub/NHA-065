# app_flask.py
from flask import Flask
from flask_cors import CORS
from config import config
from models.db import db
from routes import init_routes
from utils.firebase_auth import initialize_firebase
from utils.helpers import migrate_chat_history_schema

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

app.config.update(config.FLASK_CONFIG)
db.init_app(app)

initialize_firebase()

with app.app_context():
    db.create_all()
    migrate_chat_history_schema()

init_routes(app)

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"{config.PROJECT_NAME} v{config.VERSION}")
    print(f"ChatGPT-Style Interface")
    print(f"{'='*60}\n")
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=True)