import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import pathlib
import json
from PIL import Image
import fitz  # PyMuPDF
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# --- AI Helper Function ---
def get_gemini_response(image_parts, prompt):
    """Gets the response from the Gemini API."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt] + image_parts)
    return response.text

# --- Main Flask App ---
app = Flask(__name__)

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/process-newspaper', methods=['POST'])
def process_newspaper():
    """Handles file upload and AI processing."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            image_parts = []
            if file.filename.lower().endswith('.pdf'):
                # Handle PDF
                pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
                for page_num in range(len(pdf_doc)):
                    page = pdf_doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    image_parts.append({"mime_type": "image/png", "data": img_bytes})
                pdf_doc.close()
            else:
                # Handle Image
                img = Image.open(file.stream)
                # Convert image to a format that can be sent
                import io
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                
                image_parts.append({
                    "mime_type": "image/jpeg",
                    "data": img_byte_arr
                })

            prompt = """
            You are an expert newspaper analyst. Analyze the provided image of a Hindi news publication.
            Identify all distinct news articles. For each article, provide the following details in a JSON array of objects.
            Each object must have these exact keys and nothing else:
            1. "headline": The main headline of the article in Hindi.
            2. "category": A relevant category for the news (e.g., "राजनीति", "खेल", "मनोरंजन", "व्यापार", "स्थानीय", "दुनिया").
            3. "summary": A concise, neutral summary of the article in Hindi, in about 50-70 words.
            4. "full_text": The complete text of the article in Hindi.
            5. "formatted_text": The complete text of the article formatted nicely with HTML paragraph tags (<p>).

            Ensure the JSON is perfectly valid.
            """
            
            ai_response_text = get_gemini_response(image_parts, prompt)
            
            # Clean and parse the JSON response
            cleaned_json_text = ai_response_text.strip().replace("```json", "").replace("```", "").strip()
            articles = json.loads(cleaned_json_text)
            
            return jsonify(articles)

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", 5000))