import cv2
import os
import tkinter as tk
from tkinter import messagebox

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
DATASET_PATH = "Dataset"
if not os.path.exists(DATASET_PATH):
    os.makedirs(DATASET_PATH)
def detect_and_capture(name):
    user_dir = os.path.join(DATASET_PATH, name)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    count = 0
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            count += 1
            img_name = f"{name}_{count}.jpg"
            img_path = os.path.join(user_dir, img_name)
            cv2.imwrite(img_path, gray[y:y+h, x:x+w])
        cv2.imshow('Facial Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 50:
            break
    cap.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("Information", f"{count} images have been saved in {user_dir}")
def start_detection():
    name = name_entry.get()
    detect_and_capture(name)
root = tk.Tk()
root.title("Face Detection and Capture")
name_label = tk.Label(root, text="Enter your name:")
name_label.pack()
name_entry = tk.Entry(root)
name_entry.pack()
start_button = tk.Button(root, text="Start", command=start_detection)
start_button.pack()
root.mainloop()
