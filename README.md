# hindi_news_reader
A Python/Flask web app that uses Google Gemini AI to extract, summarize, and read aloud articles from a Hindi newspaper image.
# AI हिन्दी समाचार वाचक (AI Hindi News Reader)

This is an AI-powered web application that transforms a static image or PDF of a Hindi newspaper into an interactive and accessible experience. Users can upload a newspaper page, and the application uses the Google Gemini AI model to identify, extract, summarize, and format each news article. It features both a reading mode and an audio listening mode with play/pause controls.

---

### 🔴 Live Demo

**(Add your public Render URL here when you have it!)**
[**https://your-app-name.onrender.com**](https://your-app-name.onrender.com)

---

### ✨ Features

* **File Upload:** Accepts `.pdf`, `.jpg`, `.png`, and other common image formats.
* **AI-Powered Extraction:** Uses the Google Gemini 1.5 Flash model to intelligently identify and parse individual news articles from the image.
* **Structured Content:** For each article, the AI generates:
    * A clear headline.
    * A concise summary.
    * The full article text, formatted with HTML for readability (paragraphs, subheadings).
    * A relevant category (e.g., 'Politics', 'Sports', 'Local News').
* **Reading Mode:** View articles in a clean, card-based layout. Click to read the full, formatted text in a pop-up modal.
* **Listening Mode:** An automated audio player that reads the headline and summary of each article in sequence with a natural-sounding Hindi voice.
* **Player Controls:** Full control over the listening experience with **Play**, **Pause**, and **Stop** functionality.
* **Category Filtering:** Easily filter the displayed news articles by their category.
* **Utility Actions:** Download any article as a `.txt` file or copy its content to the clipboard.

### 🛠️ Tech Stack

* **Backend:** Python, Flask, Gunicorn
* **AI Model:** Google Gemini 1.5 Flash
* **Frontend:** HTML, Tailwind CSS, Vanilla JavaScript
* **Deployment:** Render

### 🚀 Local Setup

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  **Create a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file:** In the root of the project folder, create a file named `.env` and add your Google Gemini API key:
    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

5.  **Run the application:**
    ```bash
    python app.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

### ☁️ Deployment

This application is configured for deployment on Render. The key configuration points are:

* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `gunicorn app:app`
* **Environment Variables:** The `GEMINI_API_KEY` must be set in the Render environment dashboard for the live application to function.

### 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
