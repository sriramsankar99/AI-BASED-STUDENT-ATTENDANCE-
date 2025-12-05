from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import os

# ---------------- Home Page Window -------------------

class HomePage:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Attendance System - Home")
        self.root.geometry("1100x600")
        self.root.configure(bg="white")

        title = Label(self.root, text="AI Attendance System",
                      font=("times new roman", 32, "bold"),
                      bg="#003366", fg="white")
        title.pack(fill=X)

        subtitle = Label(self.root, text="Face Recognition Based Attendance",
                         font=("times new roman", 18, "bold"), bg="white", fg="#006699")
        subtitle.pack(pady=10)

        # ============= Buttons =============
        btn_frame = Frame(self.root, bg="white")
        btn_frame.pack(pady=40)

        btn_style = {
            "font": ("times new roman", 18, "bold"),
            "bg": "#003366",
            "fg": "white",
            "width": 20,
            "height": 2,
            "bd": 3,
            "relief": RAISED
        }

        # ---------- Functions to Open Other Files ----------
        def open_student():
            os.system("python student_details.py")

        def open_train():
            os.system("python train_data.py")

        def open_recognize():
            os.system("python face_rec.py")

        def open_attendance():
            os.system("python attendance_report.py")  # if available

        def exit_app():
            root.destroy()

        # ---------- Buttons -------------
        Button(btn_frame, text="Student Registration", command=open_student, **btn_style).grid(row=0, column=0, padx=20, pady=20)
        Button(btn_frame, text="Train Data", command=open_train, **btn_style).grid(row=0, column=1, padx=20, pady=20)
        Button(btn_frame, text="Face Recognition (Attendance)", command=open_recognize, **btn_style).grid(row=1, column=0, padx=20, pady=20)
        Button(btn_frame, text="Attendance Report", command=open_attendance, **btn_style).grid(row=1, column=1, padx=20, pady=20)
        Button(btn_frame, text="Exit", command=exit_app, **btn_style).grid(row=2, column=0, columnspan=2, pady=20)

# ---------------- Run Window -------------------
if __name__ == "__main__":
    root = Tk()
    obj = HomePage(root)
    root.mainloop()
