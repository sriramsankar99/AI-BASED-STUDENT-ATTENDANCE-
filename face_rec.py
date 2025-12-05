import tkinter as tk
from tkinter import *
from tkinter import messagebox
from time import strftime
from datetime import datetime
import mysql.connector
import cv2
import os
import numpy as np
import threading
import ttkbootstrap as tttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk


class facerecognition:

    def __init__(self, root):
        self.root = root  
        self.root.title("Face Recognition")
        self.root.geometry("1920x1080+0+0")
        self.root.configure(bg='cyan')

        # Background Image
        bg_image = Image.open("background2.jpg")
        bg_image = bg_image.resize((1920, 1080))
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.bg_label = tttk.Label(root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # UI Icon image
        ui_image = Image.open("b1.png")
        ui_image = ui_image.resize((500, 500))
        self.ui_photo = ImageTk.PhotoImage(ui_image)

        self.ui_label = tttk.Label(self.root, image=self.ui_photo)
        self.ui_label.place(x=700, y=250)

        title_Label = tttk.Label(self.root, text="FACE RECOGNITION", font=("Ariel", 30, "bold"),
                                 bootstyle="inverse-primary", anchor="center")
        title_Label.pack(fill="x", pady=10)

        style = tttk.Style()
        style.configure("primary.TButton", font=("Helvetica", 16, "bold"), padding=(10, 20))

        rec_bt = tttk.Button(self.root, text="Recognize Face", command=self.face_recognition,
                             style="primary.TButton", width=32)
        rec_bt.place(x=700, y=751)

    # ====================================================================================
    # FACE RECOGNITION FUNCTION
    # ====================================================================================

    def face_recognition(self):

        # Draw rectangle & predict face
        def draw_boundary(img, classifier, scaleFactor, minNeighbours, color, text, clf):
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbours)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)

                id, predict = clf.predict(gray_img[y:y + h, x:x + w])
                conf = int((100 * (1 - predict / 300)))

                print(f"Recognized OpenCV ID: {id}")

                # Default fallback values
                name, dept, branch, regno = "Unknown", "Unknown", "Unknown", "Unknown"

                try:
                    conn = mysql.connector.connect(
                        host="localhost",
                        username="root",
                        password="Sriram2002@mysql",
                        database="faceapp"
                    )
                    my_cur = conn.cursor()

                    # Find roll_no mapped to LBPH id
                    my_cur.execute("SELECT roll_no FROM id_mapping WHERE opencv_id = %s", (id,))
                    roll_result = my_cur.fetchone()

                    if roll_result:
                        roll_no = roll_result[0]

                        # Fetch correct student info
                        my_cur.execute("SELECT name, dept, branch, regno FROM student WHERE regno = %s", (roll_no,))
                        result = my_cur.fetchone()

                        if result:
                            name, dept, branch, regno = result

                    conn.close()

                except mysql.connector.Error as err:
                    print(f"Database Error: {err}")

                # If accuracy OK
                if conf > 80:
                    box_color = (0, 255, 0)
                    cv2.putText(img, f"Roll No: {regno}", (x, y - 75), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 0), 2)
                    cv2.putText(img, f"Name: {name}", (x, y - 55), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 0), 2)
                    cv2.putText(img, f"Dept: {dept}", (x, y - 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 0), 2)
                    cv2.putText(img, f"Branch: {branch}", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 0), 2)

                    self.mark_attendence(regno, name, dept, branch)

                else:
                    box_color = (0, 0, 255)
                    cv2.putText(img, "Unknown Face", (x, y - 55), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 0), 2)

                cv2.rectangle(img, (x, y), (x + w, y + h), box_color, 3)

            return img

        def recognize(img, clf, faceCascade):
            return draw_boundary(img, faceCascade, 1.1, 10, (0, 255, 0), "Face", clf)

        # Check Haarcascade
        if not os.path.exists("haarcascade_frontalface_default.xml"):
            print("Error: Haarcascade not found!")
            return

        faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        # Check training file
        if not os.path.exists("Train.xml"):
            print("Error: Train.xml not found!")
            return

        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read("Train.xml")

        video_capture = cv2.VideoCapture(0)

        while True:
            ret, img = video_capture.read()

            if not ret:
                print("Camera Error!")
                continue

            img = recognize(img, clf, faceCascade)
            cv2.imshow("Face Recognizer", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

    # ====================================================================================
    # ATTENDANCE MARKING
    # ====================================================================================

    def mark_attendence(self, regno, name, dept, branch):

        with open("attendence.csv", "r+", newline="\n") as f:
            myDataList = f.readlines()
            name_list = []

            for line in myDataList:
                entry = line.split(",")
                name_list.append(entry[0])

            # Avoid duplicate attendance
            if regno not in name_list:
                now = datetime.now()
                date = now.strftime("%d/%m/%Y")
                time = now.strftime("%H:%M:%S")

                f.writelines(f"\n{regno},{name},{dept},{branch},{date},{time},Present")


# MAIN WINDOW
if __name__ == "__main__":
    root = tttk.Window(themename="litera")
    obj = facerecognition(root)
    root.mainloop()
