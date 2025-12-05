from tkinter import *
from tkinter import messagebox
import os

# ------------------ Login Window ---------------------

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - AI Attendance System")
        self.root.geometry("450x350")
        self.root.configure(bg="white")

        Label(root, text="LOGIN", font=("times new roman", 28, "bold"), bg="white", fg="#003366").pack(pady=10)

        Label(root, text="Username:", font=("times new roman", 15, "bold"), bg="white").pack(pady=5)
        self.username = Entry(root, font=("times new roman", 15), bd=2, relief=SOLID)
        self.username.pack()

        Label(root, text="Password:", font=("times new roman", 15, "bold"), bg="white").pack(pady=5)
        self.password = Entry(root, font=("times new roman", 15), bd=2, relief=SOLID, show="*")
        self.password.pack()

        Button(root, text="Login", command=self.verify_login, font=("times new roman", 16, "bold"),
               bg="#003366", fg="white", width=12).pack(pady=20)

    def verify_login(self):
        user = self.username.get()
        pwd = self.password.get()

        # ---- Admin Login ----
        if user == "admin" and pwd == "admin123":
            root.destroy()
            open_home(admin=True)

        # ---- Face Recognition User Login ----
        elif user == "user" and pwd == "user123":
            root.destroy()
            open_home(admin=False)

        else:
            messagebox.showerror("Invalid Login", "Wrong Username or Password")

# ------------------ Home Page ------------------------

class HomePage:
    def __init__(self, root, admin=False):
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

        # ---------------- Functions to Open Other Files ----------------
        def open_student():
            os.system("python student_details.py")

        def open_train():
            os.system("python train_data.py")

        def open_recognize():
            os.system("python face_rec.py")

        def open_attendance():
            os.system("python attendance_report.py")

        def exit_app():
            root.destroy()

        # -------- Face Recognition Always Available --------
        Button(btn_frame, text="Face Recognition (Attendance)", command=open_recognize, **btn_style)\
            .grid(row=0, column=0, padx=20, pady=20)

        # -------- Admin Buttons Only if Login as Admin --------
        if admin:
            Button(btn_frame, text="Student Registration", command=open_student, **btn_style)\
                .grid(row=1, column=0, padx=20, pady=20)

            Button(btn_frame, text="Train Data", command=open_train, **btn_style)\
                .grid(row=1, column=1, padx=20, pady=20)

            Button(btn_frame, text="Attendance Report", command=open_attendance, **btn_style)\
                .grid(row=2, column=0, padx=20, pady=20)

        Button(btn_frame, text="Exit", command=exit_app, **btn_style)\
            .grid(row=3, column=0, pady=30)

# ------------------ Helper Function -------------------

def open_home(admin=False):
    new_root = Tk()
    HomePage(new_root, admin=admin)
    new_root.mainloop()

# ------------------ Main Program -----------------------

if __name__ == "__main__":
    root = Tk()
    LoginWindow(root)
    root.mainloop()
