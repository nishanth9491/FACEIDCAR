import cv2
import smtplib
import face_recognition
import os
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import requests
import RPi.GPIO as GPIO
import time
print("Insert the key to start the vehicle...")
# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)
# Define the GPIO pin connected to the buzzer
buzzer_pin = 18
key_pin = 17
# Set up the buzzer pin as an output
GPIO.setup(buzzer_pin, GPIO.OUT)
# Email Configuration
fromaddr = "ecsproject2023@gmail.com" # From Email ID
toaddr = "vpraneethnadh@gmail.com" # To Email ID
filename = "/home/pi/ecs_images/captured_image.jpg" # Update the file path
here
password = "fthwnahozzuooxmc" # Email Password
authorized_image_path = "/home/pi/ecs_images/4.jpg" # Update the authorized
image path here
def create_folders():
folder = '/home/pi/ecs_images'
if not os.path.exists(folder):
os.makedirs(folder)
print(f"Created folder: {folder}")
def sendEmail(latitude, longitude):
try:
print("Sending Email...")
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Unauthorized Access Detected"
body = "Unauthorized user detected. Please find the attached image and
live location for reference.\n\n"
# Add Google Maps link of the current location
google_maps_url =
f"https://www.google.com/maps?q={latitude},{longitude}"
body += f"Google Maps Location: {google_maps_url}\n"
msg.attach(MIMEText(body, 'plain'))
attachment = open(filename, "rb")
p = MIMEBase('application', 'octet-stream')
p.set_payload(attachment.read())
encoders.encode_base64(p)
p.add_header('Content-Disposition', "attachment; filename= %s" %
filename)
msg.attach(p)
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, password)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
print("Email Sent")
except Exception as e:
print("Email Sending Failed:", e)
def buzz(duration=5):
# Turn on the buzzer
GPIO.output(buzzer_pin, GPIO.HIGH)
time.sleep(duration)
# Turn off the buzzer
GPIO.output(buzzer_pin, GPIO.LOW)
def capture():
print("Capturing Photo")
cam = cv2.VideoCapture(0)
ret_val, img = cam.read()
print("Photo captured Successfully...")
# Save the captured image to the specified file path
if not os.path.exists("/home/pi/ecs_images"):
os.makedirs("/home/pi/ecs_images")
cv2.imwrite(filename, img)
cv2.destroyAllWindows()
def calculate_similarity(image1_path, image2_path):
# Load the images
image1 = face_recognition.load_image_file(image1_path)
image2 = face_recognition.load_image_file(image2_path)
# Encode the face in the images
face_encodings1 = face_recognition.face_encodings(image1)
face_encodings2 = face_recognition.face_encodings(image2)
# Check if at least one face is detected in both images
if not face_encodings1 or not face_encodings2:
print("No face detected in one or both images.")
return None
# Use the first detected face (assuming single face in the images)
face_encoding1 = face_encodings1[0]
face_encoding2 = face_encodings2[0]
# Calculate the Euclidean distance between the face encodings
distance = face_recognition.face_distance([face_encoding1],
face_encoding2)[0]
# Calculate the similarity score as a percentage
similarity_score = (1 - distance) * 100
print(similarity_score)
return similarity_score
def wait_for_key():
while True:
key_status = GPIO.input(key_pin)
if key_status == GPIO.HIGH:
print("Key Inserted! Starting main execution...")
break
if _name_ == "_main_":
# Initialize GPIO and wait for the key to be inserted
GPIO.setup(key_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
wait_for_key()
# Main execution starts only after the key is inserted
create_folders()
# Fetch public IP and location
try:
response = requests.get('https://api.ipify.org?format=json')
if response.ok:
public_ip = response.json().get('ip')
if public_ip:
url = f'https://ipinfo.io/{public_ip}/json'
response = requests.get(url)
if response.ok:
data = response.json()
location = data.get('loc')
if location:
latitude, longitude = location.split(',')
# print(f"Latitude: {latitude}, Longitude: {longitude}")
else:
print("Location not found.")
else:
print("Failed to fetch location from IP.")
else:
print("Unable to fetch public IP.")
else:
print("Failed to fetch public IP.")
except Exception as e:
print("Error fetching public IP and location:", e)
# Capture image
capture()
# Calculate similarity score
similarity_score = calculate_similarity(authorized_image_path, filename)
# You can use latitude and longitude obtained above or from GPS module
if similarity_score is not None and latitude and longitude:
print("Similarity Score:", similarity_score)
if similarity_score >= 60:
print("Authorized User...Starting Engine...")
else:
print("Unauthorized User")
sendEmail(latitude, longitude)
# Ring the buzzer for 5 seconds
buzz(5)
print("Live Location Details:")
print(f"Latitude: {latitude}")
print(f"Longitude: {longitude}")
else:
print("Error: Unable to calculate similarity score or fetch live
location.")
# Clean up the GPIO settings on program exit
GPIO.cleanup()
