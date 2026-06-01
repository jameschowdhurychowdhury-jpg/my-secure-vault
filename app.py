import os
import boto3
from botocore.client import Config
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'cyber_secure_vault_secret'

# --- BACKBLAZE B2 / S3 CREDENTIAL CONFIGURATION ---
# These will pull securely from Render's Environment Variables in production
B2_ENDPOINT_URL = os.environ.get('B2_ENDPOINT_URL', 'https://s3.us-east-005.backblazeb2.com') # Replace with your endpoint
B2_KEY_ID = os.environ.get('B2_KEY_ID', 'YOUR_B2_KEY_ID')
B2_APPLICATION_KEY = os.environ.get('B2_APPLICATION_KEY', 'YOUR_B2_APPLICATION_KEY')
B2_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME', 'YOUR_BUCKET_NAME')

# Initialize B2 Resource Client via S3-Compatible Layer
s3_client = boto3.client(
    's3',
    endpoint_url=B2_ENDPOINT_URL,
    aws_access_key_id=B2_KEY_ID,
    aws_secret_access_key=B2_APPLICATION_KEY,
    config=Config(signature_version='s3v4')
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4', 'mov', 'avi', 'doc', 'docx', 'txt', 'xlsx'}

# Dictionary mapping file types to matrix subfolders
EXTENSIONS_MAP = {
    'pictures': ['png', 'jpg', 'jpeg', 'gif'],
    'pdfs': ['pdf'],
    'videos': ['mp4', 'mov', 'avi'],
    'documents': ['doc', 'docx', 'txt', 'xlsx']
}

def get_category(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    for category, extensions in EXTENSIONS_MAP.items():
        if ext in extensions:
            return category
    return 'others'

def get_vault_data():
    """Scans the Backblaze B2 Bucket architecture to retrieve live matrix assets"""
    data = {cat: [] for cat in EXTENSIONS_MAP.keys()}
    data['others'] = []
    
    try:
        response = s3_client.list_objects_v2(Bucket=B2_BUCKET_NAME)
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                # Keys are structured as "category/filename" in the cloud bucket
                if '/' in key:
                    category, filename = key.split('/', 1)
                    if category in data and filename:
                        data[category].append(filename)
    except Exception as e:
        print(f"B2 Connection Error: {str(e)}")
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
            b2_key = f"{category}/{filename}"
            
            try:
                # Upload directly to Backblaze cloud buffer memory instead of local disk storage
                s3_client.upload_fileobj(
                    file, 
                    B2_BUCKET_NAME, 
                    b2_key,
                    ExtraArgs={'ContentType': file.content_type}
                )
                flash(f'File successfully locked into B2 Cloud Category "{category.capitalize()}"!', 'success')
            except Exception as e:
                flash(f'Matrix upload interrupted: {str(e)}', 'error')
                
            return redirect(url_for('index'))

    vault_data = get_vault_data()
    return render_template('dashboard.html', vault_data=vault_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
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
    
    b2_key = f"{category}/{filename}"
    try:
        # Fetch file data safely from Backblaze B2 cluster storage
        file_obj = s3_client.get_object(Bucket=B2_BUCKET_NAME, Key=b2_key)
        return Response(
            file_obj['Body'].read(),
            headers={"Content-Disposition": f"attachment; filename={filename}",
                     "Content-Type": file_obj.get('ContentType', 'application/octet-stream')}
        )
    except Exception as e:
        flash(f'Unable to stream file node: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<category>/<filename>', methods=['POST'])
def delete_file(category, filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    b2_key = f"{category}/{filename}"
    try:
        s3_client.delete_object(Bucket=B2_BUCKET_NAME, Key=b2_key)
        flash('File removed successfully from core Backblaze matrix cluster.', 'success')
    except Exception as e:
        flash(f'Error processing purge command: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Vault localized locks engaged. Session wiped.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)