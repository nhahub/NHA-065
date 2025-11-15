import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
from flask import request, jsonify
from config import config
import os

_initialized = False


def initialize_firebase():
    global _initialized
    if _initialized:
        return
    
    service_account_path = config.FIREBASE_SERVICE_ACCOUNT
    
    # Check if service account file exists
    if not service_account_path or not os.path.exists(service_account_path):
        print(f"Warning: Firebase service account not found at: {service_account_path}")
        return
    
    try:
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        _initialized = True
        print(f"✓ Firebase Admin SDK initialized successfully")
    except ValueError as e:
        # App already initialized
        if "already exists" in str(e).lower():
            _initialized = True
            print(f"✓ Firebase Admin SDK already initialized")
        else:
            print(f"✗ Firebase initialization error: {e}")
    except Exception as e:
        print(f"✗ Firebase initialization error: {e}")


def verify_firebase_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Expect token in Authorization header as: Bearer <idToken>
        auth_header = request.headers.get('Authorization', None)
        
        if not auth_header:
            print(f"⚠ No Authorization header provided")
            return jsonify({'success': False, 'error': 'Authorization header missing'}), 401
        
        token = auth_header.replace('Bearer ', '').strip()
        
        if not token:
            print(f"⚠ Empty token after Bearer")
            return jsonify({'success': False, 'error': 'Token is empty'}), 401
        
        try:
            initialize_firebase()
            
            if not _initialized:
                print(f"✗ Firebase not initialized properly")
                return jsonify({'success': False, 'error': 'Firebase authentication not configured'}), 500
            
            decoded = auth.verify_id_token(token)
            # Attach decoded token to request for handlers
            request.firebase_user = decoded
            print(f"✓ Token verified for user: {decoded.get('email')}")
            return f(*args, **kwargs)
            
        except auth.InvalidIdTokenError as e:
            print(f"✗ Invalid token: {e}")
            return jsonify({'success': False, 'error': 'Invalid token format', 'details': str(e)}), 401
        except auth.ExpiredIdTokenError as e:
            print(f"✗ Expired token: {e}")
            return jsonify({'success': False, 'error': 'Token has expired', 'details': str(e)}), 401
        except auth.RevokedIdTokenError as e:
            print(f"✗ Revoked token: {e}")
            return jsonify({'success': False, 'error': 'Token has been revoked', 'details': str(e)}), 401
        except Exception as e:
            print(f"✗ Token verification error: {type(e).__name__}: {e}")
            return jsonify({'success': False, 'error': 'Token verification failed', 'details': str(e)}), 401

    return decorated_function


# Helper to get UID from request (after verification)
def get_request_uid():
    user = getattr(request, 'firebase_user', None)
    if not user:
        return None
    return user.get('uid')