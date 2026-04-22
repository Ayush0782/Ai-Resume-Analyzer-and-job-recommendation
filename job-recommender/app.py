# ============================================================
# app.py — Main Flask Application
# AI-Based Job Recommendation System
# ============================================================

import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from resume_parser import extract_resume_data
from job_matcher import get_job_recommendations

# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # Max 5MB upload

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if uploaded file is a PDF."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """Serve the main frontend page."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_resume():
    """
    Main endpoint:
    1. Receives uploaded PDF
    2. Parses resume content
    3. Returns extracted skills + job recommendations
    """

    # Check if file was included in the request
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files["resume"]

    # Check if a file was actually selected
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    # Validate file type
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed."}), 400

    # Save file safely
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        # Step 1: Extract resume text and skills
        resume_data = extract_resume_data(filepath)

        # Step 2: Get job recommendations using AI matching
        recommendations = get_job_recommendations(resume_data["full_text"])

        # Step 3: Build and return response
        response = {
            "skills": resume_data["skills"],
            "keywords": resume_data["keywords"],
            "recommendations": recommendations
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

    finally:
        # Clean up: delete uploaded file after processing
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    print("Starting AI Job Recommender...")
    print("Open your browser at: http://127.0.0.1:5000")
    app.run(debug=True)
