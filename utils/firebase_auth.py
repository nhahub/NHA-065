import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
from flask import request, jsonify
import config

_initialized = False


def initialize_firebase():
    global _initialized
    if _initialized:
        return
    if not config.FIREBASE_SERVICE_ACCOUNT:
        # not configured, skip initialization
        return
    cred = credentials.Certificate(config.FIREBASE_SERVICE_ACCOUNT)
    try:
        firebase_admin.initialize_app(cred)
        _initialized = True
    except Exception:
        # app may already be initialized
        _initialized = True


def verify_firebase_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Expect token in Authorization header as: Bearer <idToken>
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authorization header missing'}), 401
        token = auth_header.replace('Bearer ', '').strip()
        try:
            initialize_firebase()
            decoded = auth.verify_id_token(token)
            # Attach decoded token to request for handlers
            request.firebase_user = decoded
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'success': False, 'error': 'Invalid or expired token', 'details': str(e)}), 401

    return decorated_function


# Helper to get UID from request (after verification)
def get_request_uid():
    user = getattr(request, 'firebase_user', None)
    if not user:
        return None
    return user.get('uid')
