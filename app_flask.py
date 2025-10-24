"""
Zypher AI Logo Generator - Flask Backend
ChatGPT-style interface with modern API
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
from PIL import Image
import io
import base64
import json

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from utils.model_manager import ModelManager
from utils.chat_history import ChatHistoryManager


app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Initialize managers
model_manager = ModelManager()
chat_history = ChatHistoryManager()


@app.route('/')
def index():
    """Serve the main ChatGPT-style interface"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate_logo():
    """
    Generate logo from prompt with optional reference image
    Endpoint: POST /api/generate
    Content-Type: multipart/form-data or application/json
    
    Form Data / JSON Body: {
        "prompt": "string",
        "use_lora": boolean,
        "num_steps": int,
        "width": int,
        "height": int,
        "use_ip_adapter": boolean (optional),
        "ip_adapter_scale": float (optional, 0.0-1.0),
        "reference_image": file (optional, for multipart/form-data)
    }
    """
    try:
        # Handle both JSON and form data
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Form data with file upload
            prompt = request.form.get('prompt', '').strip()
            use_lora = request.form.get('use_lora', 'false').lower() == 'true'
            num_steps = int(request.form.get('num_steps', 4))
            width = int(request.form.get('width', 1024))
            height = int(request.form.get('height', 1024))
            use_ip_adapter = request.form.get('use_ip_adapter', 'false').lower() == 'true'
            ip_adapter_scale = float(request.form.get('ip_adapter_scale', 0.5))
            
            # Get reference image if uploaded
            reference_image = None
            if use_ip_adapter and 'reference_image' in request.files:
                file = request.files['reference_image']
                if file and file.filename:
                    reference_image = Image.open(file.stream).convert('RGB')
        else:
            # JSON data
            data = request.json
            prompt = data.get('prompt', '').strip()
            use_lora = data.get('use_lora', False)
            num_steps = data.get('num_steps', 4)
            width = data.get('width', 1024)
            height = data.get('height', 1024)
            use_ip_adapter = data.get('use_ip_adapter', False)
            ip_adapter_scale = data.get('ip_adapter_scale', 0.5)
            
            # Handle base64 encoded reference image
            reference_image = None
            if use_ip_adapter and 'reference_image_base64' in data:
                import base64
                img_data = base64.b64decode(data['reference_image_base64'].split(',')[1])
                reference_image = Image.open(io.BytesIO(img_data)).convert('RGB')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        # Generate image
        image = model_manager.generate_image(
            prompt=prompt,
            use_lora=use_lora,
            reference_image=reference_image if use_ip_adapter else None,
            ip_adapter_scale=ip_adapter_scale if use_ip_adapter else 0.5,
            num_inference_steps=num_steps,
            width=width,
            height=height
        )
        
        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logo_{timestamp}.{config.IMAGE_FORMAT.lower()}"
        image_path = os.path.join(config.OUTPUTS_DIR, filename)
        
        if config.SAVE_GENERATED_IMAGES:
            image.save(image_path, format=config.IMAGE_FORMAT)
        
        # Convert image to base64 for response
        buffered = io.BytesIO()
        image.save(buffered, format=config.IMAGE_FORMAT)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Add to chat history
        chat_history.add_entry(prompt, image_path, use_lora)
        
        # Build model description
        model_parts = []
        if use_lora:
            model_parts.append("LoRA Fine-tuned")
        else:
            model_parts.append("Base Flux Schnell")
        if use_ip_adapter:
            model_parts.append(f"IP-Adapter ({ip_adapter_scale:.1%})")
        model_desc = " + ".join(model_parts)
        
        # Return response
        return jsonify({
            'success': True,
            'image': f"data:image/{config.IMAGE_FORMAT.lower()};base64,{img_str}",
            'filename': filename,
            'path': image_path,
            'metadata': {
                'model': model_desc,
                'steps': num_steps,
                'dimensions': f"{width}×{height}",
                'ip_adapter': use_ip_adapter,
                'ip_adapter_scale': ip_adapter_scale if use_ip_adapter else None,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get chat history"""
    try:
        history = chat_history.format_for_display()
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Clear chat history"""
    try:
        chat_history.clear_history()
        return jsonify({
            'success': True,
            'message': 'History cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/model/status', methods=['GET'])
def model_status():
    """Get model status"""
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


@app.route('/outputs/<filename>')
def serve_output(filename):
    """Serve generated images"""
    return send_from_directory(config.OUTPUTS_DIR, filename)


if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🎨 {config.PROJECT_NAME} v{config.VERSION}")
    print(f"ChatGPT-Style Interface")
    print(f"{'='*60}\n")
    
    app.run(
        host='0.0.0.0',
        port=config.SERVER_PORT,
        debug=True
    )
