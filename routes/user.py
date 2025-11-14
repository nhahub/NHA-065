# routes/user.py
from flask import Blueprint, request, jsonify, render_template
from models.db import db
from models.user import User
from utils.firebase_auth import verify_firebase_token, get_request_uid
from utils.helpers import check_and_reset_daily_limit
from config import config
from datetime import datetime

user_bp = Blueprint('user', __name__)


# In the check_and_reset_daily_limit function (wherever it is)
def check_and_reset_daily_limit(user):
    now = datetime.utcnow()  # Python datetime object
    
    if user.last_prompt_reset is None or user.last_prompt_reset.date() < now.date():
        user.prompt_count = 0
        user.last_prompt_reset = now  # Assign datetime object
        db.session.commit()
        return True
    return False

@user_bp.route('/upgrade')
def upgrade_page():
    return render_template('upgrade.html')

@user_bp.route('/api/firebase-config', methods=['GET'])
def get_firebase_config():
    """Provides the client-side Firebase config."""
    return jsonify({'success': True, 'config': config.FIREBASE_CLIENT_CONFIG })

@user_bp.route('/api/user/profile', methods=['GET'])
@verify_firebase_token
def get_user_profile():
    uid = get_request_uid()
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        fb = request.firebase_user
        return jsonify({'success': True, 'profile': {
            'fname': None, 'lname': None, 'email': fb.get('email'),
            'is_pro': False, 'prompt_count': 0, 'remaining_prompts': 5
        }})

    reset = check_and_reset_daily_limit(user)
    db.session.refresh(user)
    remaining = None if user.is_pro else (5 - user.prompt_count)

    return jsonify({'success': True, 'profile': {
        'fname': user.fname, 'lname': user.lname, 'email': user.email,
        'is_pro': user.is_pro, 'prompt_count': user.prompt_count,
        'remaining_prompts': remaining, 'reset_just_occurred': reset
    }})

@user_bp.route('/api/user/profile', methods=['POST'])
@verify_firebase_token
def update_user_profile():
    data = request.get_json() or {}
    uid = get_request_uid()
    user = User.query.filter_by(firebase_uid=uid).first_or_404()
    user.fname = data.get('fname')
    user.lname = data.get('lname')
    db.session.commit()
    return jsonify({'success': True, 'profile': {'fname': user.fname, 'lname': user.lname, 'email': user.email}})

@user_bp.route('/payment/success', methods=['POST'])
@verify_firebase_token
def payment_success():
    uid = request.firebase_user['uid']
    email = request.firebase_user.get('email', f'user_{uid}@unknown')
    user = User.query.filter_by(firebase_uid=uid).first()
    if not user:
        user = User(firebase_uid=uid, email=email)
        db.session.add(user)
        db.session.commit()
    user.is_pro = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Upgrade successful'})