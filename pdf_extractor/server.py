import os
import uuid
import tempfile
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from pdf_utils import merge_pdfs

app = Flask(__name__)
# Max file upload size of 100MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Create a temporary directory for uploads
UPLOAD_DIR = tempfile.mkdtemp(prefix="pdf_uploads_")
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        # Generate a unique ID for this uploaded file
        file_id = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
        
        file.save(filepath)
        return jsonify({
            'filename': filename,
            'id': file_id,
            'message': 'File uploaded successfully'
        })
        
    return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400

@app.route('/merge', methods=['POST'])
def merge():
    data = request.json
    if not data or 'files' not in data:
        return jsonify({'error': 'No files specified'}), 400
        
    file_ids = data['files']
    if len(file_ids) < 1:
        return jsonify({'error': 'Select at least one file to merge'}), 400
        
    user_file_paths = []
    # Verify all files exist in the upload directory
    for fid in file_ids:
        # Prevent path traversal
        clean_fid = secure_filename(fid)
        path = os.path.join(app.config['UPLOAD_FOLDER'], clean_fid)
        if os.path.exists(path):
            user_file_paths.append(path)
        else:
            return jsonify({'error': f'File {clean_fid} not found on server'}), 404
            
    # Define a temporary path for the merged output
    merged_path = os.path.join(tempfile.gettempdir(), f'merged_output_{uuid.uuid4().hex}.pdf')
    
    try:
        merge_pdfs(user_file_paths, merged_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    return send_file(
        merged_path, 
        as_attachment=True, 
        download_name='merged.pdf', 
        mimetype='application/pdf'
    )
