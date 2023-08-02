from tkinter import *
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import time
import os
import base64
import pymongo
import datetime
from datetime import datetime
import threading
import RPi.GPIO as GPIO
import evdev
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import firebase_admin
from firebase_admin import credentials, storage


from database import users_collection, logs_collection
from camera import take_capture
from email_handler import sendmail
from authentication import check_password





cred = credentials.Certificate("path-to-firebase-credentials.json")
firebase_admin.initialize_app(cred, {"storageBucket": "door-image.appspot.com"})
gpio_door = 8

dev_path = "/dev/input/by-id/usb-RFID_Reader_RFID_Reader_HF12402E73-event-kbd"
# set up the SMTP server
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "devtruong86@gmail.com"
smtp_password = "zknrdsrfqvfejtts"
GPIO.setwarnings(False)

root = Tk()

root.title("Security System ")
root.attributes("-fullscreen", True)
frame = Frame(root)
frame.pack(side=RIGHT, padx=20, pady=20, fill=Y, expand=True)
frame.grid_columnconfigure(0, weight=1)

label = Label(frame, text="Enter your password:", font=("Arial", 18), fg="black")
label.pack(pady=10)

entry = Entry(frame, font=("Arial", 18), bg="white", fg="black", show="*")
entry.pack(pady=10)

canvas = Canvas(root, bg="white")
canvas.pack(side=LEFT, expand=True, fill=BOTH)
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("face-trainer.xml")
names = {}
confidence_threshold = 80
success_threshold = 25
success_count = 0
fail_count = 0
door_opened = False

with open("person_names.txt", "r") as f:
    for line in f:
        id_, name = line.strip().split(":")
        names[int(id_)] = name
red_color = (0, 0, 255)
green_color = (0, 255, 0)

top_left = (50, 50)
top_right = (450, 50)
bottom_left = (50, 350)
bottom_right = (450, 350)

cap = cv2.VideoCapture(0)


def show_frame():
    global success_count, door_opened, fail_count

    ret, frame = cap.read()
    if ret:
        # Convert the frame to a PIL image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        # Detect faces in the image
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30)
        )

        # Resize the image to fit the canvas
        image = image.resize((canvas.winfo_width(), canvas.winfo_height()))
        # Convert the PIL image to a Tkinter-compatible image and display it on the canvas
        photo = ImageTk.PhotoImage(image=image)
        canvas.create_image(0, 0, image=photo, anchor=NW)
        canvas.photo = photo
        # Draw the fixed rectangles
        if ret:
            # Convert the frame to a PIL image
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # Detect faces in the image
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30)
            )
            # Resize the image to fit the canvas
            image = image.resize((canvas.winfo_width(), canvas.winfo_height()))
            # Convert the PIL image to a Tkinter-compatible image and display it on the canvas
            photo = ImageTk.PhotoImage(image=image)
            canvas.create_image(0, 0, image=photo, anchor=NW)
            canvas.photo = photo

            # Define the size and position of the fixed rectangle
            parent_width = canvas.winfo_width()
            parent_height = canvas.winfo_height()
            rect_width = int(0.8 * parent_width)
            rect_height = int(0.8 * parent_height)
            rect_x = int((parent_width - rect_width) / 2)
            rect_y = int((parent_height - rect_height) / 2)
            rect_coords = (rect_x, rect_y, rect_x + rect_width, rect_y + rect_height)

            # Draw the fixed rectangle
            color = "red"
            label = "No face detected"
            if len(faces) > 0:
                color = "green"
                label = "Checking..."
            canvas.create_rectangle(*rect_coords, outline=color, width=2)
            font = ("TkDefaultFont", 12, "bold")
            canvas.create_text(
                parent_width / 2, parent_height / 2, text=label, font=font, fill=color
            )

            if len(faces) > 0:
                for x, y, w, h in faces:
                    roi_gray = gray[y : y + h, x : x + w]
                    id_, conf = recognizer.predict(roi_gray)
                    if conf >= confidence_threshold:
                        label = names.get(id_, "Unknown")
                        print(f"Recognized {label} with confidence {conf}")
                        success_count += 1
                        fail_count = 0
                        if success_count >= success_threshold and not door_opened:
                            GPIO.output(gpio_door, GPIO.HIGH)
                            print(f"Door opened for {names.get(id_, 'Unknown')}")
                            messagebox.showinfo("Door Opened", f"Welcome {label}!")
                            time.sleep(5)  # keep the door open for 5 seconds
                            GPIO.output(gpio_door, GPIO.LOW)
                            success_count = 0
                            door_opened = True
                    else:
                        print(
                            "Confidence level too low ({}) - ignoring face.".format(
                                conf
                            )
                        )
                        fail_count += 1
                        if fail_count >= success_threshold:
                            messagebox.showerror(
                                "Error", "Face not recognized. Please try again."
                            )
                            time.sleep(2)
                            success_count = 0
                            fail_count = 0
                            door_opened = False
            else:
                success_count = 0
                fail_count = 0
                door_opened = False
    # Schedule the next frame refresh
    canvas.after(10, show_frame)


# Start the camera preview
show_frame()
# keyboard frame
keyboard_frame = Frame(frame)
keyboard_frame.pack(pady=10)


# create function to add a digit to the entry field
def add_digit(digit):
    if digit == "*":
        # delete the last character from the entry widget
        entry.delete(len(entry.get()) - 1, "end")
    elif digit == "#":
        on_enter(entry)

    else:
        # insert the digit into the entry widget
        entry.insert("end", digit)


# create on-screen keyboard buttons
buttons = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["*", "0", "#"]]

# add buttons to frame
for row, button_row in enumerate(buttons):
    for col, digit in enumerate(button_row):
        button = Button(
            keyboard_frame,
            text=digit,
            width=5,
            height=2,
            command=lambda digit=digit: add_digit(digit),
        )
        button.grid(row=row, column=col, padx=5, pady=5)



def on_enter(entry):
    check_password(entry)


def getDatafromMongo(filepath):
    # now = datetime.now()
    now = datetime.now()

    # check if file is empty
    is_empty = os.stat(filepath).st_size == 0
    while True:
        data = users_collection.find({"isActive": True, "expriedDate": {"$gt": now}})
        # print(data)
        if is_empty:
            with open(filepath, "w") as f:
                for item in data:
                    if "cardId" in item:
                        line = (
                            item["username"]
                            + " - "
                            + item["passcode"]
                            + " - "
                            + item["cardId"]
                            + " - "
                            + item["email"]
                            + " - "
                            + item["refUsername"]
                            + "\n"
                        )

                    else:
                        line = (
                            item["username"]
                            + " - "
                            + item["passcode"]
                            + " - NO_CARD"
                            + " - "
                            + item["email"]
                            + " - "
                            + item["refUsername"]
                            + "\n"
                        )

                    f.write(line)
        else:
            with open(filepath, "w") as f:
                for item in data:
                    if "cardId" in item:
                        line = (
                            item["username"]
                            + " - "
                            + item["passcode"]
                            + " - "
                            + item["cardId"]
                            + " - "
                            + item["email"]
                            + " - "
                            + item["refUsername"]
                            + "\n"
                        )

                    else:
                        line = (
                            item["username"]
                            + " - "
                            + item["passcode"]
                            + " - NO_CARD"
                            + " - "
                            + item["email"]
                            + " - "
                            + item["refUsername"]
                            + "\n"
                        )

                    f.write(line)
            print("->>  Getting new data .... !!!")
            # get new auto after 20 secconds
            time.sleep(10)


def read_rfid():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(gpio_door, GPIO.OUT)
    GPIO.output(gpio_door, GPIO.LOW)
    device = evdev.InputDevice(dev_path)
    # Read the input events from the USB RFID reader
    card_id = ""
    print("start reading card")
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            key_event = evdev.categorize(event)
            if key_event.keystate == key_event.key_up:
                if key_event.keycode == "KEY_ENTER":
                    found = False
                    with open("door_user.txt") as f:
                        data = f.readlines()
                    for line in data:
                        parts = line.strip().split(" - ")
                        username = parts[0]
                        passcode = parts[1]
                        cardid = parts[2]
                        email = parts[3]
                        refUser = parts[4]
                        if card_id == cardid:
                            # Display user information in a message box
                            messagebox.showinfo("Success", f"Welcome,{username}!")
                            image = take_capture()
                            
                            log = {
                                "username": username,
                                "date": datetime.now(),
                                "image": image,
                                "isOpen": True,
                                "refUsername": refUser,
                            }
                            logs_collection.insert_one(log)
                            print(" -- log saved to db -- ")                           
                            GPIO.output(gpio_door, GPIO.HIGH)
                            print("door open")

                            time.sleep(2)
                            GPIO.output(gpio_door, GPIO.LOW)
                            print("door close")
                            found = True
                            image = take_capture()
                            sendmail(username, email, image)
                            # break
                    if not found:
                        # Display "Access Denied" message in a message box
                        messagebox.showerror("Error", "User Not Found .")
                        

                    print("Please place the card")
                    card_id = ""
                else:
                    # Update message to "Card detected"
                    print("Card detected")
                    card_id += key_event.keycode[
                        4:
                    ]  # append the key value to the card ID


updateData = threading.Thread(target=getDatafromMongo, args=("door_user.txt",))
readRFID = threading.Thread(target=read_rfid)
updateData.start()
readRFID.start()

root.mainloop()
