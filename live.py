from flask import Flask, request, jsonify, send_from_directory
from gradio_client import Client, handle_file
import tempfile
import os
from flask_cors import CORS  
app = Flask(__name__, static_folder='.')
CORS(app)
@app.route('/')
def index():
    return send_from_directory('.', 'live.html')

@app.route('/api/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    temp_path = os.path.join(tempfile.gettempdir(), image_file.filename)
    image_file.save(temp_path)
    
    try:
        client = Client("maxiw/Qwen2-VL-Detection")
        result = client.predict(
            image=handle_file(temp_path),
            text_input=request.form.get('text_input', 'Just return the name of electronic device in this image'),
            system_prompt=request.form.get('system_prompt', 'You are an experienced electronic device detector'),
            model_id="Qwen/Qwen2-VL-7B-Instruct",
            api_name="/run_example"
        )
        return jsonify({'result': result[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(port=5000)