from flask import Flask, jsonify
import os

# Create a minimal Flask app to test basic functionality
app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
    <head><title>Minimal Test</title></head>
    <body>
        <h1>Flask Server Test</h1>
        <p>If you can see this, Flask is working!</p>
        <p><a href="/test">Click here to test JSON endpoint</a></p>
        <script>
            fetch('/test')
                .then(response => response.json())
                .then(data => {
                    document.body.innerHTML += '<p style="color: green;">JSON Test: ' + data.message + '</p>';
                })
                .catch(error => {
                    document.body.innerHTML += '<p style="color: red;">JSON Test Failed: ' + error.message + '</p>';
                });
        </script>
    </body>
    </html>
    """

@app.route('/test')
def test():
    """Simple test route that should return JSON"""
    return jsonify({
        "status": "success",
        "message": "Flask server is working!",
        "python_version": str(os.sys.version_info[:3])
    })

@app.route('/check-env')
def check_env():
    """Check if environment variables are accessible"""
    return jsonify({
        "env_vars": dict(os.environ),
        "gemini_key_exists": "GEMINI_API_KEY" in os.environ,
        "gemini_key_length": len(os.environ.get("GEMINI_API_KEY", "")) if "GEMINI_API_KEY" in os.environ else 0
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🔧 MINIMAL FLASK TEST SERVER")
    print("=" * 50)
    print("✅ Starting minimal server...")
    print("🌐 Will be available at: http://localhost:5000")
    print("📋 Available routes:")
    print("   / - Main test page")
    print("   /test - JSON test endpoint")
    print("   /check-env - Environment check")
    print("=" * 50)
    
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        input("Press Enter to exit...")