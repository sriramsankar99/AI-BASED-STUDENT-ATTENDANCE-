import tkinter as tk
from tkinter import messagebox
import subprocess
from login_auth import check_user_login

def login():
    u = username.get()
    p = password.get()

    user_type = check_user_login(u, p)

    if user_type == "USER":
        messagebox.showinfo("Success", "Login Successful!")
        root.destroy()
        subprocess.Popen(["python", "face_rec.py"])   # open face recognition
    else:
        messagebox.showerror("Error", "Invalid Username / Password")

root = tk.Tk()
root.title("User Login")
root.geometry("400x300")

tk.Label(root, text="User Login", font=("Arial", 18)).pack(pady=20)

tk.Label(root, text="Username").pack()
username = tk.Entry(root)
username.pack()

tk.Label(root, text="Password").pack()
password = tk.Entry(root, show="*")
password.pack()

tk.Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()
