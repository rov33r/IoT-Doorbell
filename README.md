# IoT-Doorbell
An IoT-based face-recognition doorbell built with a Raspberry Pi 4, webcam, and components from an Arduino kit.
When the doorbell button is pressed, the system rings a buzzer, captures an image, sends it to AWS Rekognition for face matching, and lights up a green LED if the visitor is recognized, otherwise, it blinks red.

## Hardware Components

- **Raspberry Pi 4** – Acts as the main processing unit and runs the Flask web server.
- **Webcam** – Captures live images when the doorbell button is pressed.
- **Button (from Arduino kit)** – Triggers the image capture and recognition process.
- **Buzzer (from Arduino kit)** – Provides an audible notification when the button is pressed.

---

## Software & Services

- **Flask** – Web framework used to run the local server and handle image uploads.
- **AWS Rekognition** – Cloud service that compares the captured image with a stored reference image to identify the person.
- **AWS S3** – Used to store reference images for known faces.
- **Python** – Main programming language integrating all components and services.

---

## System Architecture

1. The **Raspberry Pi 4** hosts a **Flask server** that handles incoming image uploads from the connected webcam.
2. When the **button** is pressed:
   - The **buzzer** sounds to indicate the system is active.
   - The **webcam** captures an image and sends it to the Flask backend.
3. The Flask server uploads the image to **AWS Rekognition** for comparison with a **reference image** stored in **S3**.
4. **Rekognition** returns a similarity score:
   - If the person is **recognized**, the **green LED** blinks.
   - If the person is **not recognized**, the **red LED** blinks.
5. The result is displayed in the Flask web interface, accessible via the Raspberry Pi’s local network IP.

---

## How It Works

1. Start the Flask server on the Raspberry Pi.
2. Press the button connected to the Pi’s GPIO pins.
3. The webcam captures an image and sends it to the Flask app.
4. The app communicates with **AWS Rekognition**, which analyzes the face and compares it with the stored reference image in **S3**.
5. Based on the recognition result:
   - **Recognized:** Green LED blinks.
   - **Unrecognized:** Red LED blinks.
6. The recognition result is logged and shown on the Flask web page.
