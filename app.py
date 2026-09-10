import os
import boto3
from botocore.client import Config
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
from werkzeug.utils import secure_filename
from datetime import timedelta
from functools import wraps

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "cyber_secure_vault_secret"
)

# Configure session cookies for proper cross-browser and Render compatibility
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
)
app.config['SESSION_COOKIE_NAME'] = 'secure_vault_session'

B2_ENDPOINT_URL = os.environ.get('B2_ENDPOINT_URL', 'https://s3.us-east-005.backblazeb2.com')
B2_KEY_ID = os.environ.get('B2_KEY_ID', 'YOUR_B2_KEY_ID')
B2_APPLICATION_KEY = os.environ.get('B2_APPLICATION_KEY', 'YOUR_B2_APPLICATION_KEY')
B2_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME', 'YOUR_BUCKET_NAME')

config = Config(
    signature_version="s3v4",
    connect_timeout=5,
    read_timeout=10,
    retries={
        "max_attempts": 2
    }
)

s3_client = boto3.client(
    "s3",
    endpoint_url=B2_ENDPOINT_URL,
    aws_access_key_id=B2_KEY_ID,
    aws_secret_access_key=B2_APPLICATION_KEY,
    config=config
)

EXTENSIONS_MAP = {
    'pictures': ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
    'pdfs': ['pdf'],
    'videos': ['mp4', 'mov', 'avi', 'mkv', 'flv', 'webm'],
    'documents': ['doc', 'docx', 'txt', 'xlsx', 'xls', 'ppt', 'pptx']
}

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_category(filename):
    """Get file category based on extension"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    for category, extensions in EXTENSIONS_MAP.items():
        if ext in extensions:
            return category
    return 'others'

def get_vault_data():
    """Fetch all files from S3 and organize by category"""
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
                
                file_info = {
                    'filename': filename, 
                    'key': key,
                    'size': obj.get('Size', 0),
                    'last_modified': obj.get('LastModified', '')
                }
                
                if category in data:
                    data[category].append(file_info)
                else:
                    data['others'].append(file_info)
        
        # Sort files by last modified (newest first)
        for category in data:
            data[category].sort(
                key=lambda x: x['last_modified'], 
                reverse=True
            )
            
    except Exception as e:
        print(f"B2 Connection Error: {str(e)}")
        flash(f"System Diagnostic Error (B2 Scan): {str(e)}", "error")
        
    return data

def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Main dashboard - display vault contents"""
    
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
            
            # Prevent empty filename
            if not filename:
                flash('Invalid filename.', 'error')
                return redirect(request.url)
            
            category = get_category(filename)
            b2_key = f"{category}/{filename}"
            
            try:
                s3_client.upload_fileobj(
                    file, 
                    B2_BUCKET_NAME, 
                    b2_key, 
                    ExtraArgs={'ContentType': file.content_type}
                )
                flash(f'✅ File successfully uploaded to "{category.capitalize()}"!', 'success')
            except Exception as e:
                flash(f'❌ Upload failed: {str(e)}', 'error')
                
            return redirect(url_for('index'))

    vault_data = get_vault_data()
    return render_template("dashboard.html", vault_data=vault_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate credentials
        if username == 'James' and password == '03102010':
            session.permanent = True
            session['logged_in'] = True
            session.modified = True

            flash('✅ Welcome back! Vault unlocked.', 'success')
            return redirect(url_for('index'))
        else:
            flash('❌ Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/view')
@login_required
def view_file():
    """View file in browser"""
    
    b2_key = request.args.get('key')
    if not b2_key:
        return redirect(url_for('index'))
        
    try:
        file_obj = s3_client.get_object(Bucket=B2_BUCKET_NAME, Key=b2_key)
        return Response(
            file_obj['Body'].read(),
            headers={
                "Content-Disposition": "inline",
                "Content-Type": file_obj.get('ContentType', 'application/octet-stream')
            }
        )
    except Exception as e:
        flash(f'❌ View failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download')
@login_required
def download_file():
    """Download file from vault"""
    
    b2_key = request.args.get('key')
    if not b2_key:
        return redirect(url_for('index'))
        
    filename = b2_key.split('/')[-1]
    try:
        file_obj = s3_client.get_object(Bucket=B2_BUCKET_NAME, Key=b2_key)
        return Response(
            file_obj['Body'].read(),
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": file_obj.get('ContentType', 'application/octet-stream')
            }
        )
    except Exception as e:
        flash(f'❌ Download failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
@login_required
def delete_file():
    """Delete file from vault"""
    
    b2_key = request.form.get('key')
    if not b2_key:
        flash('❌ No file specified for deletion.', 'error')
        return redirect(url_for('index'))
        
    try:
        s3_client.delete_object(Bucket=B2_BUCKET_NAME, Key=b2_key)
        filename = b2_key.split('/')[-1]
        flash(f'✅ File "{filename}" deleted successfully.', 'success')
    except Exception as e:
        flash(f'❌ Delete failed: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/rename', methods=['POST'])
@login_required
def rename_file():
    """Rename file in vault"""
    
    old_key = request.form.get('old_key')
    new_name = request.form.get('new_name', '').strip()

    if not old_key or not new_name:
        flash("❌ Please enter a valid filename.", "error")
        return redirect(url_for('index'))

    # Secure filename
    new_name = secure_filename(new_name)

    # Keep original extension
    old_filename = old_key.split('/')[-1]
    old_ext = os.path.splitext(old_filename)[1]

    if not new_name.lower().endswith(old_ext.lower()):
        new_name += old_ext

    category = old_key.split('/')[0]
    new_key = f"{category}/{new_name}"

    try:
        # Prevent duplicate names
        try:
            s3_client.head_object(
                Bucket=B2_BUCKET_NAME,
                Key=new_key
            )
            flash("❌ A file with that name already exists.", "error")
            return redirect(url_for('index'))
        except:
            pass

        # Copy object
        s3_client.copy_object(
            Bucket=B2_BUCKET_NAME,
            CopySource={
                "Bucket": B2_BUCKET_NAME,
                "Key": old_key
            },
            Key=new_key
        )

        # Delete original
        s3_client.delete_object(
            Bucket=B2_BUCKET_NAME,
            Key=old_key
        )

        flash(f"✅ File renamed successfully!", "success")

    except Exception as e:
        flash(f"❌ Rename failed: {str(e)}", "error")

    return redirect(url_for('index'))

@app.route('/search')
@login_required
def search_files():
    """Search for files (API endpoint)"""
    
    query = request.args.get('q', '').lower()
    vault_data = get_vault_data()
    results = []
    
    for category, files in vault_data.items():
        for file in files:
            if query in file['filename'].lower():
                results.append({
                    'filename': file['filename'],
                    'category': category,
                    'key': file['key'],
                    'size': format_file_size(file['size'])
                })
    
    return jsonify(results)

@app.route('/stats')
@login_required
def get_stats():
    """Get vault statistics (API endpoint)"""
    
    vault_data = get_vault_data()
    stats = {
        'total_files': sum(len(files) for files in vault_data.values()),
        'total_size': 0,
        'categories': {}
    }
    
    for category, files in vault_data.items():
        total_size = sum(file.get('size', 0) for file in files)
        stats['categories'][category] = {
            'count': len(files),
            'size': format_file_size(total_size)
        }
        stats['total_size'] += total_size
    
    stats['total_size'] = format_file_size(stats['total_size'])
    return jsonify(stats)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('✅ Logged out successfully. Vault locked.', 'success')
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    flash('❌ Page not found.', 'error')
    return redirect(url_for('index') if session.get('logged_in') else url_for('login'))

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    flash('❌ An unexpected error occurred.', 'error')
    return redirect(url_for('index') if session.get('logged_in') else url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
