import RPi.GPIO as GPIO
import time
from tkinter import messagebox
from datetime import datetime

from email_handler import sendmail
from database import users_collection,logs_collection
from camera import take_capture

gpio_door = 8

GPIO.setwarnings(False)

def check_password(entry):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(gpio_door, GPIO.OUT)
    GPIO.output(gpio_door, GPIO.LOW)
    password = entry.get().strip()
    password_found = False
    # open file read data
    with open("door_user.txt") as f:
        data = f.readlines()
    for line in data:
        parts = line.strip().split(" - ")
        username = parts[0]
        stored_password = parts[1]
        email = parts[3]
        refUser = parts[4]
        if password == stored_password:
            entry.delete(0, "end")
            messagebox.showinfo("Success", f"Welcome, {username}!")
            GPIO.output(gpio_door, GPIO.HIGH)
            print("door open")

            image = take_capture()

            log = {
                "username": username,
                "date": datetime.now(),
                "image": image,
                "isOpen": True,
                "refUsername": refUser,
            }
            logs_collection.insert_one(log)
            print(" -- log saved to db ")
            print("waiting for 5 seconds to close door !")
            print("email send")
            time.sleep(2)
            GPIO.output(gpio_door, GPIO.LOW)
            print("door close")
            password_found = True
            sendmail(username, email, image)
            return
    if not password_found:
        entry.delete(0, "end")
        print("access denied !!")
        messagebox.showerror("Error", "User Not Found .")
        print(" -- log saved to db ")
