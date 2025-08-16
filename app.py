import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import pathlib
import json
from PIL import Image # Pillow library to handle images
import fitz # PyMuPDF for handling PDFs

# --- Configuration ---
# Create a .env file in the same directory and add your key like this:
# GEMINI_API_KEY="YOUR_API_KEY_HERE"
from dotenv import load_dotenv
load_dotenv()

# Configure the Gemini API key
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    # This is a fallback for environments where .env is not used.
    # It's better to handle this gracefully.
    print("ERROR: GEMINI_API_KEY not found in environment variables.")
    print("Please create a .env file and add your API key.")
    exit()


# --- Flask App Setup ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'pdf'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Helper Functions ---
def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_images(pdf_path):
    """Convert the first page of a PDF to a PIL Image."""
    try:
        doc = fitz.open(pdf_path)
        # We only process the first page as requested
        page = doc.load_page(0) 
        pix = page.get_pixmap(dpi=150) # Render page to an image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return [img]
    except Exception as e:
        print(f"Error converting PDF to image: {e}")
        return None

# --- AI Model Interaction ---
def get_gemini_response(image_parts):
    """
    Sends image parts to Gemini and gets a structured JSON response.
    """
    # Model configuration
    generation_config = {
        "temperature": 0.2,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json", # Crucial for structured output
    }
    
    # Safety settings to allow a wide range of news content
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", # Using Flash for speed and cost-effectiveness
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    # The detailed prompt for the AI
    prompt = """
    You are an expert newspaper analyst specializing in Hindi newspapers.
    Analyze the provided image of a newspaper page. Identify each distinct news article.
    For each article, extract the following information and return it as a JSON object.
    The final output should be a JSON array of these objects.
    
    Order the articles in the array based on their position on the page: from top to bottom, and left to right.

    For each article, provide a JSON object with these exact keys:
    1.  "headline": The main headline of the article in Hindi.
    2.  "summary": A concise, easy-to-understand summary of the full article in about 50-70 words, in Hindi.
    3.  "full_text": The complete, verbatim text of the article in Hindi.
    4.  "category": Categorize the article into one of the following topics: 'राजनीति' (Politics), 'खेल' (Sports), 'मनोरंजन' (Entertainment), 'व्यापार' (Business), 'प्रौद्योगिकी' (Technology), 'स्थानीय समाचार' (Local News), 'अंतर्राष्ट्रीय' (International), 'स्वास्थ्य' (Health), 'शिक्षा' (Education), 'अन्य' (Other).

    Ensure the entire output is a single, valid JSON array. Do not include any text or markdown formatting before or after the JSON array.
    """

    try:
        # The request combines the prompt and the image(s)
        response = model.generate_content([prompt] + image_parts)
        # Clean up the response text to ensure it's valid JSON
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as e:
        print(f"An error occurred during Gemini API call: {e}")
        # It's possible the model returns an error message as text instead of JSON
        print(f"Gemini Raw Response: {response.text if 'response' in locals() else 'No response object'}")
        return {"error": f"AI model failed to process the content. Details: {str(e)}"}


# --- Flask Routes ---
@app.route('/')
def index():
    """Render the main HTML page."""
    return render_template('index.html')

@app.route('/process-newspaper', methods=['POST'])
def process_newspaper():
    """
    Handle the file upload, process it with AI, and return the articles.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if not (file and allowed_file(file.filename)):
        return jsonify({"error": "File type not allowed"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Use a try...finally block to ensure the file is always deleted
    try:
        image_parts = []
        if filename.lower().endswith('.pdf'):
            images = pdf_to_images(filepath)
            if not images:
                return jsonify({"error": "Could not process the PDF file."}), 500
            image_parts.append(images[0])
        else:
            # Use 'with' to ensure the image file is properly closed
            with Image.open(filepath) as image:
                image_parts.append(image.copy()) # Use .copy() as the image data is needed after 'with' block

        # Send to Gemini for processing
        ai_response = get_gemini_response(image_parts)
        
        if "error" in ai_response:
             return jsonify(ai_response), 500

        return jsonify(ai_response)

    except Exception as e:
        # Catch any other unexpected errors during processing
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected server error occurred: {str(e)}"}), 500
    finally:
        # This code will run whether the 'try' block succeeds or fails
        if os.path.exists(filepath):
            os.remove(filepath)

  

# --- Main Execution ---
if __name__ == '__main__':
    # Using debug=True is fine for development, but should be False in production
    app.run(debug=True)
