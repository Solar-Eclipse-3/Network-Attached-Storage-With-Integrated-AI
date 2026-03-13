import os
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)

# Configuration
STORAGE_PATH = Path("storage")
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx',
    'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm'  # Video formats
}

# Create storage directory if it doesn't exist
STORAGE_PATH.mkdir(exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(STORAGE_PATH / filename)
        return jsonify({'message': f'File {filename} uploaded successfully'}), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_file(STORAGE_PATH / secure_filename(filename))
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/list', methods=['GET'])
def list_files():
    files = [f.name for f in STORAGE_PATH.iterdir() if f.is_file()]
    return jsonify({'files': files})

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_path = STORAGE_PATH / secure_filename(filename)
        file_path.unlink()
        return jsonify({'message': f'File {filename} deleted successfully'}), 200
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    # Run on all network interfaces (0.0.0.0) to allow external connections
    # Use threaded=True to handle multiple connections
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True) 