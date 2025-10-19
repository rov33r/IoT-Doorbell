import eventlet
import os
from flask import Flask, render_template, request, send_from_directory, jsonify, url_for
from flask_socketio import SocketIO, emit
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Directory to save images temporarily
IMAGE_DIR = 'images'
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# AWS S3 and Rekognition setup
S3_BUCKET_NAME = '373bucket'
REKOGNITION_IMAGE_KEY = 'group6/me.JPG'  # The image to compare to in S3
ACCESS_KEY = ''
SECRET_KEY = ''
REGION = 'us-east-1'

# Setup Rekognition client
rekognition_client = boto3.client('rekognition', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name=REGION)

latest_image_filename = None

@app.route('/')
def index():
    global latest_image_filename
    # Set default placeholder image if no image is uploaded yet
    image_url = url_for('get_image', filename=latest_image_filename) if latest_image_filename else url_for('static', filename='images/placeholder.jpg')
    return render_template('indexxx.html', image_url=image_url)

@app.route('/image/<filename>')
def get_image(filename):
    try:
        file_path = os.path.join(os.path.abspath(IMAGE_DIR), filename)
        print(f"Serving file: {file_path}")
        return send_from_directory(os.path.abspath(IMAGE_DIR), filename)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return jsonify({"error": "Image not found"}), 404

@app.route('/upload_image', methods=['POST'])
def upload_image():
    global latest_image_filename
    if 'image' not in request.files:
        return jsonify({'status': 'fail', 'message': 'No image part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'status': 'fail', 'message': 'No selected file'}), 400

    # Save the file with a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"door_{timestamp}.jpg"
    file_path = os.path.join(IMAGE_DIR, filename)

    try:
        file.save(file_path)
        latest_image_filename = filename
        print(f"Image saved at: {file_path}")

        # Notify web clients about the new image
        socketio.emit('new_image', {'image_url': url_for('get_image', filename=filename)})

        # Compare the saved image with the reference image in S3
        match_found = compare_with_rekognition(file_path)

        # Return the result without uploading the image to S3
        if match_found:
            return jsonify({'status': 'success', 'filename': filename, 'command': 'Allow'}), 200
        else:
            return jsonify({'status': 'success', 'filename': filename, 'command': 'Deny'}), 200
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'status': 'fail', 'message': 'Error saving file'}), 500

def compare_with_rekognition(file_path):
    try:
        # Open the captured image
        with open(file_path, 'rb') as image_file:
            target_image_bytes = image_file.read()

        # Call Rekognition to compare faces
        response = rekognition_client.compare_faces(
            SourceImage={'S3Object': {'Bucket': S3_BUCKET_NAME, 'Name': REKOGNITION_IMAGE_KEY}},
            TargetImage={'Bytes': target_image_bytes},
            SimilarityThreshold=80
        )

        if response['FaceMatches']:
            similarity = response['FaceMatches'][0]['Similarity']
            print(f"Face match found with {similarity}% similarity")
            return similarity >= 80
        else:
            print("No face match found")
            return False
    except Exception as e:
        print(f"Error comparing images with Rekognition: {e}")
        return False

def upload_to_s3(file_path, filename):
    try:
        s3_key = f"group6/pictures/{filename}"
        s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY, region_name=REGION)
        s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        print(f"Image {filename} uploaded to S3 under {s3_key}")
        return True
    except NoCredentialsError:
        print("Credentials not available")
        return False
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    if latest_image_filename:
        emit('new_image', {'image_url': url_for('get_image', filename=latest_image_filename)})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    host_ip = "194.47.453.66"
    port = 5001
    print(f"Server is running. Access the interface at: http://{host_ip}:{port}")
    socketio.run(app, host=host_ip, port=port, debug=True)