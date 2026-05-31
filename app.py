import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'cyber_secure_vault_secret'

# Setup local storage folders matching your file tree
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4', 'mov', 'avi', 'doc', 'docx', 'txt', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dictionary mapping file types to subfolders
EXTENSIONS_MAP = {
    'pictures': ['png', 'jpg', 'jpeg', 'gif'],
    'pdfs': ['pdf'],
    'videos': ['mp4', 'mov', 'avi'],
    'documents': ['doc', 'docx', 'txt', 'xlsx']
}

# Ensure folders exist
for category in EXTENSIONS_MAP.keys():
    os.makedirs(os.path.join(UPLOAD_FOLDER, category), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'others'), exist_ok=True)

def get_category(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    for category, extensions in EXTENSIONS_MAP.items():
        if ext in extensions:
            return category
    return 'others'

def get_vault_data():
    """Scans upload directories to pass live file arrays into your template variables"""
    data = {cat: [] for cat in EXTENSIONS_MAP.keys()}
    data['others'] = []
    
    for category in data.keys():
        category_path = os.path.join(UPLOAD_FOLDER, category)
        if os.path.exists(category_path):
            data[category] = [f for f in os.listdir(category_path) if os.path.isfile(os.path.join(category_path, f))]
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part detected.', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file chosen.', 'error')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            category = get_category(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], category, filename))
            flash(f'File successfully locked into "{category.capitalize()}"!', 'success')
            return redirect(url_for('index'))

    vault_data = get_vault_data()
    return render_template('dashboard.html', vault_data=vault_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hardcoded matching to match your placeholder visual assets
        if username == 'SYS_ADMIN' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('ACCESS DENIED: Invalid Matrix Cipher Key credentials.', 'error')
            
    return render_template('login.html')

@app.route('/download/<category>/<filename>')
def download_file(category, filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], category), filename)

@app.route('/delete/<category>/<filename>', methods=['POST'])
def delete_file(category, filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], category, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash('File removed successfully from core matrix.', 'success')
        else:
            flash('File target context location not found.', 'error')
    except Exception as e:
        flash(f'Error processing command: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Vault localized locks engaged. Session wiped.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)