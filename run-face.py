import cv2
import numpy as np
import os
from PIL import Image

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

Face_ID = -1 
pev_person_name = ""
y_ID = []
x_train = []

Face_Images = os.path.join(os.getcwd(), "Dataset") 
total_images = sum([len(files) for root, dirs, files in os.walk(Face_Images)])

for root, dirs, files in os.walk(Face_Images): 
    for i,file in enumerate(files): 
        if file.endswith("jpeg") or file.endswith("jpg") or file.endswith("png"): 
            path = os.path.join(root, file)
            person_name = os.path.basename(root)
            print(f"Processing image {i+1}/{total_images} for person {person_name}")
            if pev_person_name!=person_name:
                Face_ID=Face_ID+1 
                pev_person_name = person_name
            Gery_Image = Image.open(path).convert("L") 
            Crop_Image = Gery_Image.resize( (800,800) , Image.LANCZOS)
            Final_Image = np.array(Crop_Image, "uint8")
            faces = face_cascade.detectMultiScale(Final_Image, scaleFactor=1.3, minNeighbors=5) 
            for (x,y,w,h) in faces:
                roi = Final_Image[y:y+h, x:x+w] 
                x_train.append(roi)
                y_ID.append(Face_ID)
                
recognizer.train(x_train, np.array(y_ID)) 
recognizer.write("face-trainer.xml") 
print('Training completed successfully.')
print('Saved data to : face-trainer.xml ')
print('Saved data to : person_names.txt ')
# Write person names and IDs to a text file
with open('person_names.txt', 'w') as f:
    for root, dirs, files in os.walk(Face_Images):
        for i, dir in enumerate(dirs):
            f.write(f"{i}: {dir}\n")