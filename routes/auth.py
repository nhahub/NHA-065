# routes/auth.py
from flask import Blueprint, render_template, send_from_directory
import os
from config import config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login')
def login_page():
    return render_template('login.html')

@auth_bp.route('/signup')
def signup_page():
    return render_template('signup.html')

# Serve custom static photos (favicon, logo, etc.)
@auth_bp.route('/photos/<path:filename>')
def serve_photos(filename):
    photos_dir = os.path.join(config.BASE_DIR, 'photos')
    return send_from_directory(photos_dir, filename)