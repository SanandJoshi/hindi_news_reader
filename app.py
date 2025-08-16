import os
import json
import uuid
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
# This is the shared folder where the Web App and Background Worker will communicate.
# On Render, you will set this path to the mount point of your persistent disk, e.g., "/var/data/shared"
SHARED_DIR = Path(os.getenv("SHARED_DIR", "shared"))
UPLOADS_DIR = SHARED_DIR / "uploads"
JOBS_DIR = SHARED_DIR / "jobs"
RESULTS_DIR = SHARED_DIR / "results"

# Create directories if they don't exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
JOBS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/process-newspaper', methods=['POST'])
def process_newspaper():
    """
    Handles the file upload.
    This function is now VERY FAST. It just saves the file and creates a job.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        
        # Generate a unique ID for this job
        job_id = str(uuid.uuid4())
        
        # Save the uploaded file to the shared uploads directory
        saved_filepath = UPLOADS_DIR / f"{job_id}_{filename}"
        file.save(saved_filepath)
        
        # Create a job file. The worker will look for this file.
        job_filepath = JOBS_DIR / f"{job_id}.json"
        with open(job_filepath, 'w') as f:
            json.dump({"job_id": job_id, "original_filename": filename, "filepath": str(saved_filepath)}, f)
            
        # Instantly return the job ID to the user
        return jsonify({"job_id": job_id, "status": "processing"}), 202

@app.route('/get-result/<job_id>', methods=['GET'])
def get_result(job_id):
    """
    Checks if the background worker has finished processing the job.
    The frontend will call this repeatedly.
    """
    result_filepath = RESULTS_DIR / f"{job_id}.json"
    
    if result_filepath.exists():
        # The job is done! Read the result and send it back.
        with open(result_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Optional: Clean up the files after retrieving the result
        # os.remove(result_filepath) 
        # You might also want to clean up the original upload and job file.
        
        return jsonify(data)
    else:
        # Job is not ready yet.
        return jsonify({"status": "processing"}), 202

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", 5000))