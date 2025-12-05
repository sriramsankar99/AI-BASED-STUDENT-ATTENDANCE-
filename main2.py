from tkinter import *
import os

class HomePage:
    def __init__(self, root, access):
        self.root = root
        self.root.title("AI Attendance System - Home")
        self.root.geometry("1100x600")
        self.root.configure(bg="white")

        Label(self.root, text="AI Attendance System",
              font=("times new roman", 32, "bold"), bg="#003366", fg="white").pack(fill=X)

        Label(self.root, text="Face Recognition Based Attendance",
              font=("times new roman", 18, "bold"), bg="white", fg="#006699").pack(pady=10)

        btn_frame = Frame(self.root, bg="white")
        btn_frame.pack(pady=40)

        btn_style = {"font": ("times new roman", 18, "bold"), "bg": "#003366",
                     "fg": "white", "width": 20, "height": 2, "bd": 3, "relief": RAISED}

        if access == "admin":   # Admin full access
            Button(btn_frame, text="Student Registration", command=lambda: os.system("python student_details.py"), **btn_style).grid(row=0, column=0, padx=20, pady=20)
            Button(btn_frame, text="Train Data", command=lambda: os.system("python train_data.py"), **btn_style).grid(row=0, column=1, padx=20, pady=20)

        Button(btn_frame, text="Face Recognition (Attendance)", command=lambda: os.system("python face_rec.py"), **btn_style).grid(row=1, column=0, padx=20, pady=20)
        Button(btn_frame, text="Attendance Report", command=lambda: os.system("python attendance_report.py"), **btn_style).grid(row=1, column=1, padx=20, pady=20)

        Button(btn_frame, text="Exit", command=self.root.destroy,
               **btn_style).grid(row=2, column=0, columnspan=2, pady=20)


def open_home(access):
    root = Tk()
    HomePage(root, access)
    root.mainloop()

