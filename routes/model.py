# routes/model.py
from flask import Blueprint, jsonify
from utils.model_manager import ModelManager

model_bp = Blueprint('model', __name__, url_prefix='/api/model')

# Global instance – shared across requests
model_manager = ModelManager()


@model_bp.route('/status', methods=['GET'])
def model_status():
    """Return info about the loaded diffusion model."""
    try:
        info = model_manager.get_model_info()
        return jsonify({
            'success': True,
            'model': info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_bp.route('/loras', methods=['GET'])
def list_loras():
    """List all available LoRA files and the currently active one."""
    try:
        loras = model_manager.get_available_loras()
        current = model_manager.current_lora
        return jsonify({
            'success': True,
            'loras': loras,
            'current_lora': current,
            'count': len(loras)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500