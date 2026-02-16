from flask import Flask, render_template, request, send_file, flash
from flask_wtf.csrf import CSRFProtect
from forms import TextForm, FileForm
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
import base64
import os
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-change-in-prod-2026')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
csrf = CSRFProtect(app)
app.config['WTF_CSRF_TIME_LIMIT'] = None

def generate_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, 
                     iterations=100000, backend=default_backend())
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

@app.route("/", methods=["GET", "POST"])
def home():
    text_form = TextForm()
    file_form = FileForm()
    result = ""
    
    # TEXT ENCRYPTION/DECRYPTION
    if text_form.is_submitted() and request.form.get("action"):
        if text_form.validate():
            text = text_form.text.data
            password = text_form.password.data
            action = request.form.get("action")
            
            try:
                if action == "encrypt":
                    salt = os.urandom(16)
                    key = generate_key(password, salt)
                    cipher = Fernet(key)
                    encrypted = cipher.encrypt(text.encode())
                    result = base64.b64encode(salt + encrypted).decode()
                    flash("Encrypted successfully! ✅", "success")
                elif action == "decrypt":
                    decoded = base64.b64decode(text)
                    salt = decoded[:16]
                    encrypted = decoded[16:]
                    key = generate_key(password, salt)
                    cipher = Fernet(key)
                    decrypted = cipher.decrypt(encrypted)
                    result = decrypted.decode()
                    flash("Decrypted successfully! ✅", "success")
            except Exception:
                flash("❌ Wrong password or corrupted data!", "error")
    
    # FILE ENCRYPTION/DECRYPTION
    elif request.method == "POST" and request.form.get("file_action"):
        if 'file' not in request.files:
            flash("No file selected!", "error")
        else:
            file = request.files['file']
            password = request.form.get('password')
            action = request.form.get("file_action")
            
            if file.filename == '':
                flash("No file selected!", "error")
            elif not password:
                flash("Password required!", "error")
            else:
                file_data = file.read()
                try:
                    if action == "encrypt":
                        salt = os.urandom(16)
                        key = generate_key(password, salt)
                        cipher = Fernet(key)
                        encrypted = cipher.encrypt(file_data)
                        output = salt + encrypted
                        filename = f"encrypted_{secure_filename(file.filename)}"
                    elif action == "decrypt":
                        if len(file_data) < 16:
                            raise Exception()
                        salt = file_data[:16]
                        encrypted = file_data[16:]
                        key = generate_key(password, salt)
                        cipher = Fernet(key)
                        output = cipher.decrypt(encrypted)
                        filename = f"decrypted_{secure_filename(file.filename)}"
                    
                    return send_file(
                        BytesIO(output),
                        as_attachment=True,
                        download_name=filename
                    )
                except Exception:
                    flash("❌ Wrong password or corrupted file!", "error")
    
    return render_template("index.html", text_form=text_form, file_form=file_form, result=result)

if __name__ == "__main__":
    app.run(debug=True)
