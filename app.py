import os
import boto3
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'employees')

# Get background image URL from ConfigMap
BACKGROUND_IMAGE_URL = os.environ.get('BACKGROUND_IMAGE_URL', '')
STUDENT_NAME = os.environ.get('STUDENT_NAME', 'Your Name')

# AWS S3 Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
S3_BUCKET = os.environ.get('S3_BUCKET', '')

mysql = MySQL(app)

# Function to download image from S3
def download_image_from_s3():
    try:
        if BACKGROUND_IMAGE_URL and S3_BUCKET:
            s3_client = boto3.client('s3', region_name=AWS_REGION)
            
            # Extract filename from URL
            image_filename = BACKGROUND_IMAGE_URL.split('/')[-1]
            local_path = f"static/{image_filename}"
            
            # Download image from S3
            s3_client.download_file(S3_BUCKET, image_filename, local_path)
            
            logger.info(f"Background image downloaded: {BACKGROUND_IMAGE_URL}")
            return f"/{local_path}"
    except Exception as e:
        logger.error(f"Error downloading image from S3: {str(e)}")
        return None

@app.route('/')
def index():
    # Download background image
    background_image_path = download_image_from_s3()
    
    return render_template('index.html', 
                         student_name=STUDENT_NAME,
                         background_image=background_image_path)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO employees (name, email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('index'))
    
    background_image_path = download_image_from_s3()
    return render_template('add.html', 
                         student_name=STUDENT_NAME,
                         background_image=background_image_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)