from utils.cloud_upload import upload_to_s3, generate_presigned_url
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.file_handler import extract_text
from utils.predictor import predict_sensitivity
from utils.encryptor import encrypt_file

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, send_file
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

UPLOAD_FOLDER = 'uploads'
DECRYPTED_FOLDER = 'decrypted'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

app = Flask(__name__)

# Configuration
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)

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

            # Upload to S3 and store link in session
            upload_to_s3(encrypted_path, enc_filename)
            presigned_url = generate_presigned_url(enc_filename)
            session['download_url'] = presigned_url

            flash(f"Sensitive file detected and encrypted: {enc_filename}")
        else:
            session.pop('enc_file', None)
            session.pop('download_url', None)
            flash("File is not sensitive. Uploaded as is.")

        return redirect(url_for('home'))
    else:
        flash('Unsupported file type.')
        return redirect(url_for('home'))

@app.route('/download')
def download_file():
    url = session.get('download_url')
    if url:
        return redirect(url)
    else:
        flash("No download link available.")
        return redirect(url_for('home'))

def detect_file_extension(data):
    if data.startswith(b'%PDF'):
        return '.pdf'
    elif data.startswith(b'PK') and b'word/' in data:
        return '.docx'
    elif all(32 <= b <= 126 or b in (9, 10, 13) for b in data[:100]):
        return '.txt'
    return '.bin'

def decrypt_file_and_guess_extension(input_path, key):
    try:
        with open(input_path, 'rb') as f:
            iv = f.read(16)
            ciphered_data = f.read()

        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ciphered_data), AES.block_size)
        ext = detect_file_extension(decrypted_data)

        output_filename = os.path.basename(input_path).replace('.enc', '') + ext
        output_path = os.path.join(DECRYPTED_FOLDER, output_filename)

        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

        return output_path
    except Exception as e:
        print(f"[Decryption Error] {e}")
        return None

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        file = request.files.get('file')
        key = request.form.get('key')

        if not file or not key:
            flash("Missing file or key.")
            return redirect(url_for('decrypt'))

        filename = secure_filename(file.filename)
        if not filename.endswith('.enc'):
            flash("Only .enc files are supported.")
            return redirect(url_for('decrypt'))

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        output_path = decrypt_file_and_guess_extension(filepath, key)

        if output_path:
            return send_file(output_path, as_attachment=True)
        else:
            flash("Decryption failed. Invalid key or corrupted file.")
            return redirect(url_for('decrypt'))

    return render_template('decrypt.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
