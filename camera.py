import cv2
import time
import os
from firebase_admin import storage

cap = cv2.VideoCapture(0)

def take_capture():
    _, frame = cap.read()
    if not os.path.exists("Images"):
        os.mkdir("Images")
    filename = "Images/{}.png".format(int(time.time()))
    cv2.imwrite(filename, frame)

    bucket = storage.bucket()
    blob = bucket.blob(os.path.basename(filename))
    blob.upload_from_filename(filename)

    blob.make_public()
    url = blob.public_url

    print(f"Uploaded image to Firebase Storage: {url}")

    return url
