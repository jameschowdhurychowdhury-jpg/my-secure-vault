import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- CONFIGURATION ---
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_session_key_change_this_anytime')
PASSWORD = "James@2010"  # Your master vault password

# --- BACKBLAZE B2 / S3 CREDENTIALS ---
B2_KEY_ID = os.environ.get('B2_KEY_ID')
B2_APPLICATION_KEY = os.environ.get('B2_APPLICATION_KEY')
B2_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME')
B2_ENDPOINT_URL = os.environ.get('B2_ENDPOINT_URL', 'https://s3.us-west-004.backblazeb2.com')

# AUTO-FIX: If the environment variable is missing 'https://', add it automatically
if B2_ENDPOINT_URL and not B2_ENDPOINT_URL.startswith(('http://', 'https://')):
    B2_ENDPOINT_URL = f"https://{B2_ENDPOINT_URL}"

# Initialize the S3-compatible client for Backblaze B2 connection
s3_client = boto3.client(
    's3',
    endpoint_url=B2_ENDPOINT_URL,
    aws_access_key_id=B2_KEY_ID,
    aws_secret_access_key=B2_APPLICATION_KEY
)

# File categories mapping
SECTIONS = {
    'pictures': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'],
    'pdfs': ['.pdf'],
    'videos': ['.mp4', '.mov', '.avi', '.mkv', '.wmv'],
    'documents': ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv']
}

def get_section_for_file(filename):
    _, ext = os.path.splitext(filename.lower())
    for section, extensions in SECTIONS.items():
        if ext in extensions:
            return section
    return 'others'

# --- ROUTING & FLOW CONTROL ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect password. Access Denied.', 'danger')
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part found', 'warning')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'warning')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            target_section = get_section_for_file(filename)
            cloud_storage_key = f"{target_section}/{filename}"
            
            try:
                s3_client.upload_fileobj(file, B2_BUCKET_NAME, cloud_storage_key)
                flash(f'"{filename}" safely backed up to {target_section.capitalize()} cloud room!', 'success')
            except ClientError as e:
                flash(f"Cloud write failure: {e}", "danger")
                
            return redirect(url_for('dashboard'))

    vault_data = {'pictures': [], 'pdfs': [], 'videos': [], 'documents': [], 'others': []}
    try:
        response = s3_client.list_objects_v2(Bucket=B2_BUCKET_NAME)
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                if '/' in key:
                    category, filename = key.split('/', 1)
                    if category in vault_data:
                        vault_data[category].append(filename)
                    else:
                        vault_data['others'].append(filename)
    except ClientError as e:
        flash(f"Error fetching directory index from Cloud: {e}", "danger")

    return render_template('dashboard.html', vault_data=vault_data)


@app.route('/uploads/<category>/<filename>')
def download_file(category, filename):
    if not session.get('logged_in'):
        return "Unauthorized", 401
        
    cloud_storage_key = f"{category}/{filename}"
    try:
        file_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': B2_BUCKET_NAME, 'Key': cloud_storage_key},
            ExpiresIn=3600
        )
        return redirect(file_url)
    except ClientError as e:
        return f"Error retrieving cloud object: {e}", 500


@app.route('/delete/<category>/<filename>', methods=['POST'])
def delete_file(category, filename):
    if not session.get('logged_in'):
        return "Unauthorized", 401
    
    cloud_storage_key = f"{category}/{filename}"
    try:
        s3_client.delete_object(Bucket=B2_BUCKET_NAME, Key=cloud_storage_key)
        flash(f'"{filename}" permanently destroyed from storage cluster.', 'info')
    except ClientError as e:
        flash(f"Cloud removal error: {e}", "danger")
        
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out safely.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)