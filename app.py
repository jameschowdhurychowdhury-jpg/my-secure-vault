import os
import boto3
from botocore.client import Config
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from werkzeug.utils import secure_filename
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'cyber_secure_vault_secret'

# Configure session cookies for proper cross-browser and Render compatibility
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cross-site cookies
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SECURE'] = True  # Set to True for HTTPS (Render uses HTTPS)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_NAME'] = 'secure_vault_session'

B2_ENDPOINT_URL = os.environ.get('B2_ENDPOINT_URL', 'https://s3.us-east-005.backblazeb2.com')
B2_KEY_ID = os.environ.get('B2_KEY_ID', 'YOUR_B2_KEY_ID')
B2_APPLICATION_KEY = os.environ.get('B2_APPLICATION_KEY', 'YOUR_B2_APPLICATION_KEY')
B2_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME', 'YOUR_BUCKET_NAME')

s3_client = boto3.client(
    's3',
    endpoint_url=B2_ENDPOINT_URL,
    aws_access_key_id=B2_KEY_ID,
    aws_secret_access_key=B2_APPLICATION_KEY,
    config=Config(signature_version='s3v4')
)

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
    data = {cat: [] for cat in EXTENSIONS_MAP.keys()}
    data['others'] = []
    
    try:
        response = s3_client.list_objects_v2(Bucket=B2_BUCKET_NAME)
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                if key.endswith('/'):  
                    continue
                
                filename = key.split('/')[-1]
                category = get_category(filename)
                
                file_info = {'filename': filename, 'key': key}
                if category in data:
                    data[category].append(file_info)
                else:
                    data['others'].append(file_info)
    except Exception as e:
        print(f"B2 Connection Error: {str(e)}")
        from flask import flash
        flash(f"System Diagnostic Error (B2 Scan): {str(e)}", "error")
        
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
                s3_client.upload_fileobj(file, B2_BUCKET_NAME, b2_key, ExtraArgs={'ContentType': file.content_type})
                flash(f'File successfully uploaded to "{category.capitalize()}"!', 'success')
            except Exception as e:
                flash(f'Upload failed: {str(e)}', 'error')
                
            return redirect(url_for('index'))

    return render_template('dashboard.html', vault_data=get_vault_data())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'James' and password == '03102010':
            session.permanent = True
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/download')
def download_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    b2_key = request.args.get('key')
    if not b2_key:
        return redirect(url_for('index'))
        
    filename = b2_key.split('/')[-1]
    try:
        file_obj = s3_client.get_object(Bucket=B2_BUCKET_NAME, Key=b2_key)
        return Response(
            file_obj['Body'].read(),
            headers={"Content-Disposition": f"attachment; filename={filename}",
                     "Content-Type": file_obj.get('ContentType', 'application/octet-stream')}
        )
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/view')
def view_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    b2_key = request.args.get('key')
    if not b2_key:
        return redirect(url_for('index'))
        
    try:
        file_obj = s3_client.get_object(Bucket=B2_BUCKET_NAME, Key=b2_key)
        return Response(
            file_obj['Body'].read(),
            headers={"Content-Disposition": "inline",
                     "Content-Type": file_obj.get('ContentType', 'application/octet-stream')}
        )
    except Exception as e:
        flash(f'View failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete_file():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    b2_key = request.form.get('key')
    if not b2_key:
        return redirect(url_for('index'))
        
    try:
        s3_client.delete_object(Bucket=B2_BUCKET_NAME, Key=b2_key)
        flash('File deleted successfully.', 'success')
    except Exception as e:
        flash(f'Delete failed: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
