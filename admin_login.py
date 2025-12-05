import tkinter as tk
from tkinter import messagebox
import subprocess
from login_auth import check_user_login

def login():
    u = username.get()
    p = password.get()

    user_type = check_user_login(u, p)

    if user_type == "ADMIN":
        messagebox.showinfo("Success", "Admin Login Successful!")
        root.destroy()
        open_admin_menu()
    else:
        messagebox.showerror("Error", "Invalid Username / Password")

def open_admin_menu():
    admin = tk.Tk()
    admin.title("Admin Dashboard")
    admin.geometry("400x400")

    tk.Label(admin, text="Admin Dashboard", font=("Arial", 18)).pack(pady=20)

    tk.Button(admin, text="Student Details",
              command=lambda: subprocess.Popen(["python", "student_details.py"]),
              width=30).pack(pady=10)

    tk.Button(admin, text="Train Data",
              command=lambda: subprocess.Popen(["python", "train_data.py"]),
              width=30).pack(pady=10)

    tk.Button(admin, text="Attendance Report",
              command=lambda: subprocess.Popen(["python", "attendence.py"]),
              width=30).pack(pady=10)

    admin.mainloop()

root = tk.Tk()
root.title("Admin Login")
root.geometry("400x300")

tk.Label(root, text="Admin Login", font=("Arial", 18)).pack(pady=20)

tk.Label(root, text="Username").pack()
username = tk.Entry(root)
username.pack()

tk.Label(root, text="Password").pack()
password = tk.Entry(root, show="*")
password.pack()

tk.Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()
