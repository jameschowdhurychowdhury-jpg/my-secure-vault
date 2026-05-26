import os
import io
import mimetypes
from functools import wraps
import boto3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-vault-key")

# --- BACKBLAZE B2 CONFIGURATION ---
B2_BUCKET_NAME = os.environ.get("B2_BUCKET_NAME")
VAULT_PASSWORD = os.environ.get("VAULT_PASSWORD", "password123")

s3_client = boto3.client(
    's3',
    endpoint_url=os.environ.get('B2_ENDPOINT_URL'),
    aws_access_key_id=os.environ.get('B2_KEY_ID'),
    aws_secret_access_key=os.environ.get('B2_APPLICATION_KEY'),
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-005')
)

# --- SECURITY DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_password = request.form.get('password')
        if input_password == VAULT_PASSWORD:
            session['logged_in'] = True
            session.permanent = True
            return redirect(url_for('index'))
        else:
            flash("Incorrect master password. Access denied.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    categories = {
        'pictures': [],
        'pdfs': [],
        'videos': [],
        'documents': [],
        'others': []
    }
    
    try:
        response = s3_client.list_objects_v2(Bucket=B2_BUCKET_NAME)
        files = response.get('Contents', [])
        
        for f in files:
            filename = f['Key']
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                categories['pictures'].append(filename)
            elif ext == '.pdf':
                categories['pdfs'].append(filename)
            elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                categories['videos'].append(filename)
            elif ext in ['.txt', '.docx', '.xlsx', '.pptx', '.csv', '.md']:
                categories['documents'].append(filename)
            else:
                categories['others'].append(filename)
                
    except Exception as e:
        flash(f"Error fetching directory index from Cloud: {str(e)}", "danger")

    return render_template('index.html', categories=categories)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash("No file selected.", "warning")
        return redirect(url_for('index'))
        
    file = request.files['file']
    if file.filename == '':
        flash("No file selected.", "warning")
        return redirect(url_for('index'))

    if file:
        filename = file.filename
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'application/octet-stream'

        try:
            s3_client.upload_fileobj(
                file,
                B2_BUCKET_NAME,
                filename,
                ExtraArgs={'ContentType': mime_type}
            )
            flash(f"'{filename}' successfully uploaded directly to vault.", "success")
        except Exception as e:
            flash(f"Cloud write failure: {str(e)}", "danger")
            
    return redirect(url_for('index'))

@app.route('/view/<path:filename>')
@login_required
def view_file(filename):
    try:
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'application/octet-stream'

        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': B2_BUCKET_NAME,
                'Key': filename,
                'ResponseContentDisposition': 'inline',
                'ResponseContentType': mime_type
            },
            ExpiresIn=3600
        )
        return redirect(url)
    except Exception as e:
        flash(f"Could not generate preview link: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': B2_BUCKET_NAME,
                'Key': filename,
                'ResponseContentDisposition': f'attachment; filename="{filename}"'
            },
            ExpiresIn=3600
        )
        return redirect(url)
    except Exception as e:
        flash(f"Could not generate download link: {str(e)}", "danger")
        return redirect(url_for('index'))

# --- NEW: SECURE CLOUD DELETION ROUTE ---
@app.route('/delete/<path:filename>', methods=['POST'])
@login_required
def delete_file(filename):
    try:
        s3_client.delete_object(Bucket=B2_BUCKET_NAME, Key=filename)
        flash(f"'{filename}' was permanently deleted from your storage vault.", "success")
    except Exception as e:
        flash(f"Failed to remove file from cloud storage: {str(e)}", "danger")
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)