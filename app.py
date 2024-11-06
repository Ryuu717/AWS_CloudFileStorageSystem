from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import boto3
from config import Config
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Needed for flashing messages
app.config.from_object(Config)

# Initialize Boto3 S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=app.config['AWS_ACCESS_KEY'],
                  aws_secret_access_key=app.config['AWS_SECRET_KEY'],
                  region_name=app.config['REGION'])

# Home Route - List files and show upload form
@app.route('/')
def index():
    # Fetch the list of files from S3 bucket
    try:
        objects = s3.list_objects_v2(Bucket=app.config['S3_BUCKET'])
        files = [obj['Key'] for obj in objects.get('Contents', [])]
    except Exception as e:
        print(f"Error fetching files: {e}")
        files = []
    
    return render_template('index.html', files=files)

# Upload Route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part provided!', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected!', 'danger')
        return redirect(url_for('index'))
    
    filename = secure_filename(file.filename)
    
    # Upload file to S3 bucket
    try:
        s3.upload_fileobj(file, app.config['S3_BUCKET'], filename)
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Failed to upload file: {e}', 'danger')
        return redirect(url_for('index'))

# Download Route
@app.route('/download/<filename>')
def download_file(filename):
    # Download the file from S3 bucket
    try:
        file_obj = s3.get_object(Bucket=app.config['S3_BUCKET'], Key=filename)
        file_data = file_obj['Body'].read()
        
        # Return file as downloadable attachment
        flash('File downloaded successfully!', 'success')
        return send_file(BytesIO(file_data),
                         download_name=filename,
                         as_attachment=True)
    except Exception as e:
        flash(f'Failed to download file: {e}', 'danger')
        return redirect(url_for('index'))

# Delete Route
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    # Delete the file from S3 bucket
    try:
        s3.delete_object(Bucket=app.config['S3_BUCKET'], Key=filename)
        flash('File deleted successfully!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Failed to delete file: {e}', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
