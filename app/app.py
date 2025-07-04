from dotenv import load_dotenv
from utils.cloud_upload import upload_to_s3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.file_handler import extract_text
from utils.predictor import predict_sensitivity
from utils.encryptor import encrypt_file

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

app = Flask(__name__)
load_dotenv()


# Configuration
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('home'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('home'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        text = extract_text(filepath)
        if "ERROR" in text:
            flash('Error processing file.')
            return redirect(url_for('home'))

        prediction = predict_sensitivity(text)

        if prediction == 1:
            encrypted_path, _ = encrypt_file(filepath)
            enc_filename = os.path.basename(encrypted_path)
            session['enc_file'] = enc_filename
            flash(f"Sensitive file detected and encrypted: {enc_filename}")

            # ✅ AWS S3 Upload
            aws_key = "AKIA3FLD4IHSRSMOZQ66"
            aws_secret = "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"
            bucket_name = "cloud-dlp-uploads-07"
            s3_url = upload_to_s3(encrypted_path, bucket_name, enc_filename, aws_key, aws_secret)
            flash(f"Encrypted file uploaded to S3: {s3_url}")
        else:
            session.pop('enc_file', None)
            flash("File is not sensitive. Uploaded as is.")

        return redirect(url_for('home'))
    else:
        flash('Unsupported file type.')
        return redirect(url_for('home'))

@app.route('/download')
def download_file():
    enc_file = session.get('enc_file')
    if not enc_file:
        flash("No encrypted file available for download.")
        return redirect(url_for('home'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], enc_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
