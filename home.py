# home.py — Full single-file upgraded Home page
# Requires: pillow, pygame, pyttsx3, customtkinter
# Place in same folder as your project scripts and assets.
# Uses uploaded background (if available):
# /mnt/data/face_attendance/Face_attendence/background.jpg

import os
import sys
import time
import math
import random
import subprocess
from pathlib import Path
from datetime import datetime
from threading import Thread

# try preferred UI lib, otherwise fallback to tkinter (but customtkinter gives best look)
try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except Exception:
    CTK_AVAILABLE = False
    import tkinter as tk

from PIL import Image, ImageTk, ImageFilter, ImageOps

# optional libs
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

# ---------------------- Configuration ----------------------
# Use uploaded background path first (from your session)
UPLOADED_BG = Path("/mnt/data/face_attendance/Face_attendence/background.jpg")
LOCAL_BG = Path("background.jpg")
BACKGROUND_PATH = UPLOADED_BG if UPLOADED_BG.exists() else (LOCAL_BG if LOCAL_BG.exists() else None)

CLICK_SOUND = Path("click.wav")    # put click.wav in same folder if you want sound
USER_ICON = Path("user_icon.png")  # optional icon
ADMIN_ICON = Path("admin_icon.png")# optional icon

# Script names found in your uploaded project (fallback tolerant)
FACE_REC_SCRIPT = Path("face_rec.py")                 # will be launched for recognition
ALT_FACE_REC = Path("face_recognition.py")            # fallback
ATTENDANCE_SCRIPT = Path("attendence.py")             # spelled as in your upload
STUDENT_SCRIPT = Path("student_details.py")           # student details
TRAIN_SCRIPT = Path("train_data.py")                  # training script

# UI tuning
GLASS_WIDTH, GLASS_HEIGHT = 760, 420
NUM_PARTICLES = 28
LOADING_SECONDS = 1.6

# ---------------------- Helper functions ----------------------
def run_script_nonblocking(script_path):
    # tries to launch script with same python executable
    if script_path.exists():
        try:
            return subprocess.Popen([sys.executable, str(script_path)])
        except Exception as e:
            print("Failed to launch", script_path, e)
    else:
        print("Script not found:", script_path)
    return None

def try_launch_face_rec():
    # try common names
    if FACE_REC_SCRIPT.exists():
        return run_script_nonblocking(FACE_REC_SCRIPT)
    if ALT_FACE_REC.exists():
        return run_script_nonblocking(ALT_FACE_REC)
    print("No face recognition script found.")
    return None

def play_click():
    if PYGAME_AVAILABLE and CLICK_SOUND.exists():
        try:
            s = pygame.mixer.Sound(str(CLICK_SOUND))
            s.play()
        except Exception:
            pass

def speak(text):
    if not TTS_AVAILABLE:
        return
    def _s():
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception:
            pass
    Thread(target=_s, daemon=True).start()

def pil_open(path, size=None):
    try:
        im = Image.open(path).convert("RGBA")
        if size:
            im = ImageOps.fit(im, size, Image.LANCZOS)
        return im
    except Exception:
        return None

# ---------------------- UI Setup ----------------------
if CTK_AVAILABLE:
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("dark-blue")
    App = ctk.CTk
    Frame = ctk.CTkFrame
    Label = ctk.CTkLabel
    Button = ctk.CTkButton
    Toplevel = ctk.CTkToplevel
else:
    import tkinter as tk
    App = tk.Tk
    Frame = tk.Frame
    Label = tk.Label
    Button = tk.Button
    Toplevel = tk.Toplevel

app = App()
app.title("Smart Face Attendance System")
# Start fullscreen for modern look but you can resize; user wanted always visible home, so we will not destroy it.
try:
    app.attributes("-fullscreen", True)
except Exception:
    pass

screen_w = app.winfo_screenwidth()
screen_h = app.winfo_screenheight()

# ---------------------- Canvas and Background ----------------------
# Use a canvas to draw particles and frosted panel image
if CTK_AVAILABLE:
    canvas = ctk.CTkCanvas(app, width=screen_w, height=screen_h, highlightthickness=0)
else:
    import tkinter as tk
    canvas = tk.Canvas(app, width=screen_w, height=screen_h, highlightthickness=0)
canvas.pack(fill="both", expand=True)

bg_pil = None
bg_tk = None
if BACKGROUND_PATH:
    try:
        bg_pil = pil_open(BACKGROUND_PATH, size=(screen_w, screen_h))
        if bg_pil:
            bg_tk = ImageTk.PhotoImage(bg_pil)
            canvas.create_image(0, 0, anchor="nw", image=bg_tk)
    except Exception as e:
        print("Background load error:", e)

if bg_tk is None:
    canvas.configure(bg="#0f1724")  # fallback dark

# ---------------------- Particles ----------------------
class Particle:
    def __init__(self, canvas, w, h):
        self.canvas = canvas
        self.w, self.h = w, h
        self.r = random.randint(6, 26)
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(0.25, 1.2)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed * 0.35
        shade = random.randint(150, 255)
        self.fill = f"#{shade:02x}{shade:02x}{shade:02x}"
        # stipple not supported in all canvases; we use simple shapes
        self.id = self.canvas.create_oval(self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r,
                                          fill=self.fill, outline="")

    def step(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < -60: self.x = self.w + 60
        if self.x > self.w + 60: self.x = -60
        if self.y < -60: self.y = self.h + 60
        if self.y > self.h + 60: self.y = -60
        self.canvas.coords(self.id, self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)

particles = [Particle(canvas, screen_w, screen_h) for _ in range(NUM_PARTICLES)]
def animate_particles():
    for p in particles:
        p.step()
    app.after(40, animate_particles)
app.after(100, animate_particles)

# ---------------------- Frosted glass panel (crop & blur) ----------------------
panel_cx = screen_w // 2
panel_cy = int(screen_h * 0.56)
def create_frosted_image(cx, cy, w, h, blur_radius=12, darken=0.28):
    if bg_pil is None:
        im = Image.new("RGBA", (w, h), (255,255,255,int(255*(1-darken))))
    else:
        left = max(0, int(cx - w//2))
        top = max(0, int(cy - h//2))
        right = min(bg_pil.width, left + w)
        bottom = min(bg_pil.height, top + h)
        crop = bg_pil.crop((left, top, right, bottom)).resize((w, h), Image.LANCZOS)
        blurred = crop.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        overlay = Image.new("RGBA", (w,h), (10,10,10,int(255*darken)))
        im = Image.alpha_composite(blurred, overlay)
    return ImageTk.PhotoImage(im)

frost_img = create_frosted_image(panel_cx, panel_cy, GLASS_WIDTH, GLASS_HEIGHT)
panel_img_id = canvas.create_image(panel_cx - GLASS_WIDTH//2, panel_cy - GLASS_HEIGHT//2, anchor="nw", image=frost_img)
canvas.create_rectangle(panel_cx - GLASS_WIDTH//2, panel_cy - GLASS_HEIGHT//2,
                        panel_cx + GLASS_WIDTH//2, panel_cy + GLASS_HEIGHT//2,
                        outline="#ffffff40", width=2)

# ---------------------- Container for widgets over panel ----------------------
if CTK_AVAILABLE:
    container = ctk.CTkFrame(app, fg_color="transparent", corner_radius=12)
else:
    container = Frame(app, bg="")

container_win = canvas.create_window(panel_cx, panel_cy, window=container, anchor="center")

# Title & subtitle
if CTK_AVAILABLE:
    title_lbl = ctk.CTkLabel(container, text="SMART FACE ATTENDANCE SYSTEM",
                              font=ctk.CTkFont(size=28, weight="bold"))
    subtitle_lbl = ctk.CTkLabel(container, text="Secure • Fast • Smart", font=ctk.CTkFont(size=14))
else:
    title_lbl = Label(container, text="SMART FACE ATTENDANCE SYSTEM", font=("Times New Roman", 28, "bold"), bg="")
    subtitle_lbl = Label(container, text="Secure • Fast • Smart", font=("Arial", 12), bg="")

title_lbl.place(relx=0.5, rely=0.12, anchor="center")
subtitle_lbl.place(relx=0.5, rely=0.20, anchor="center")

# ---------------------- Clock & Date ----------------------
if CTK_AVAILABLE:
    clock_lbl = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=13))
else:
    clock_lbl = Label(app, text="", font=("Arial", 12), bg="")

canvas.create_window(int(screen_w*0.12), int(screen_h*0.06), window=clock_lbl, anchor="w")

def update_clock():
    now = datetime.now()
    clock_lbl.configure(text=now.strftime("%A, %d %B %Y    %I:%M:%S %p"))
    app.after(1000, update_clock)
update_clock()

# ---------------------- Load icons ----------------------
def load_icon(path, size=(54,54)):
    im = pil_open(path, size)
    return ImageTk.PhotoImage(im) if im else None

user_icon_tk = load_icon(USER_ICON, (54,54))
admin_icon_tk = load_icon(ADMIN_ICON, (54,54))

# ---------------------- Hover button factory ----------------------
def make_button(master, text, command, relx, rely, icon=None):
    # Use CTkButton if available for neat look
    if CTK_AVAILABLE:
        btn = ctk.CTkButton(master, text=text, width=300, height=52, corner_radius=12,
                            fg_color="#1976d2", hover_color="#2196f3",
                            command=command, anchor="w",
                            font=ctk.CTkFont(size=15, weight="bold"))
        if icon:
            btn.configure(image=icon, compound="left", padx=12)
    else:
        btn = Button(master, text=text, width=28, height=2, bg="#1976d2", fg="white",
                     font=("Arial", 12, "bold"), command=command, cursor="hand2")
    btn.place(relx=relx, rely=rely, anchor="center")
    # subtle hover resize
    def on_enter(e):
        try:
            btn.configure(width=320)
        except Exception:
            pass
    def on_leave(e):
        try:
            btn.configure(width=300)
        except Exception:
            pass
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

# ---------------------- Loading overlay ----------------------
overlay_refs = {}
def show_loading_and_launch(script_path):
    # semi-transparent overlay
    overlay = Image.new("RGBA", (screen_w, screen_h), (6,10,20,180))
    overlay_tk = ImageTk.PhotoImage(overlay)
    ov_id = canvas.create_image(0,0, anchor="nw", image=overlay_tk)
    overlay_refs['ov'] = overlay_tk

    # frame
    w, h = 520, 120
    x0, y0 = screen_w//2 - w//2, screen_h//2 - h//2
    frame_img = Image.new("RGBA", (w,h), (255,255,255,18))
    frame_tk = ImageTk.PhotoImage(frame_img)
    fr_id = canvas.create_image(x0, y0, anchor="nw", image=frame_tk)
    overlay_refs['fr'] = frame_tk

    txt_id = canvas.create_text(screen_w//2, screen_h//2 - 12, text="Preparing...", fill="#ffffff",
                                font=("Arial", 16, "bold"))
    pb_x = screen_w//2 - int(w*0.9)//2
    pb_y = screen_h//2 + 12
    pb_w = int(w*0.9)
    pb_h = 16
    canvas.create_rectangle(pb_x, pb_y, pb_x + pb_w, pb_y + pb_h, fill="#2b2b2b", outline="")
    prog = canvas.create_rectangle(pb_x, pb_y, pb_x, pb_y+pb_h, fill="#4fc3f7", outline="")

    start = time.time()
    def step():
        t = time.time() - start
        frac = min(1.0, t / LOADING_SECONDS)
        cw = int(pb_w * frac)
        canvas.coords(prog, pb_x, pb_y, pb_x + cw, pb_y + pb_h)
        canvas.itemconfigure(txt_id, text=f"Starting... {int(frac*100)}%")
        if frac < 1.0:
            app.after(20, step)
        else:
            # cleanup
            canvas.delete(ov_id); canvas.delete(fr_id); canvas.delete(txt_id); canvas.delete(prog)
            # launch script
            if script_path:
                run_script_nonblocking(script_path)
    step()

# ---------------------- User & Admin windows (non-modal) ----------------------
def open_user_window():
    play_click()
    speak("Welcome user. Please login to start face recognition.")
    # create non-modal Toplevel; do NOT use grab_set or focus_force
    win = Toplevel(app)
    win.title("User Login")
    win.geometry("520x420+420+140")
    try:
        win.attributes("-topmost", True)
        win.after(200, lambda: win.attributes("-topmost", False))
    except Exception:
        pass

    # content
    if CTK_AVAILABLE:
        header = ctk.CTkLabel(win, text="User Login", font=ctk.CTkFont(size=20, weight="bold"))
    else:
        header = Label(win, text="User Login", font=("Arial", 18, "bold"))
    header.pack(pady=(18,6))

    if user_icon_tk:
        img_lbl = Label(win, image=user_icon_tk, bg=None if CTK_AVAILABLE else win['bg'])
        img_lbl.pack(pady=(6,8))

    # fields
    if CTK_AVAILABLE:
        entry_user = ctk.CTkEntry(win, placeholder_text="Username", width=380)
        entry_pass = ctk.CTkEntry(win, placeholder_text="Password", width=380, show="*")
    else:
        entry_user = Entry(win, width=40)
        entry_pass = Entry(win, width=40, show="*")
    entry_user.pack(pady=6); entry_pass.pack(pady=6)

    def start_face():
        # optionally implement authentication here; we'll show loading then launch face_rec
        show_loading_and_launch(FACE_REC_SCRIPT if FACE_REC_SCRIPT.exists() else (ALT_FACE_REC if ALT_FACE_REC.exists() else None))

    if CTK_AVAILABLE:
        start_btn = ctk.CTkButton(win, text="Start Face Recognition", width=360, command=start_face)
        close_btn = ctk.CTkButton(win, text="Close", width=120, fg_color="#9e9e9e", command=win.destroy)
    else:
        start_btn = Button(win, text="Start Face Recognition", width=30, height=2, bg="#1976d2", fg="white", command=start_face)
        close_btn = Button(win, text="Close", width=12, bg="#9e9e9e", command=win.destroy)

    start_btn.pack(pady=16)
    close_btn.pack(pady=(8,18))

def open_admin_window():
    play_click()
    speak("Welcome admin. Opening dashboard.")
    win = Toplevel(app)
    win.title("Admin Dashboard")
    win.geometry("520x520+440+160")
    try:
        win.attributes("-topmost", True)
        win.after(200, lambda: win.attributes("-topmost", False))
    except Exception:
        pass

    if CTK_AVAILABLE:
        header = ctk.CTkLabel(win, text="Admin Dashboard", font=ctk.CTkFont(size=20, weight="bold"))
    else:
        header = Label(win, text="Admin Dashboard", font=("Arial", 18, "bold"))
    header.pack(pady=(12,6))

    if admin_icon_tk:
        Label(win, image=admin_icon_tk).pack(pady=(6,10))

    def launch_att():
        play_click()
        run_script_nonblocking(ATTENDANCE_SCRIPT)

    def launch_student():
        play_click()
        run_script_nonblocking(STUDENT_SCRIPT)

    def launch_train():
        play_click()
        run_script_nonblocking(TRAIN_SCRIPT)

    if CTK_AVAILABLE:
        ctk.CTkButton(win, text="Attendance Report", width=360, command=launch_att).pack(pady=10)
        ctk.CTkButton(win, text="Student Details", width=360, command=launch_student).pack(pady=10)
        ctk.CTkButton(win, text="Train Dataset", width=360, command=launch_train).pack(pady=10)
        ctk.CTkButton(win, text="Close", width=140, fg_color="#9e9e9e", command=win.destroy).pack(pady=16)
    else:
        Button(win, text="Attendance Report", width=30, height=2, command=launch_att).pack(pady=10)
        Button(win, text="Student Details", width=30, height=2, command=launch_student).pack(pady=10)
        Button(win, text="Train Dataset", width=30, height=2, command=launch_train).pack(pady=10)
        Button(win, text="Close", width=14, bg="#9e9e9e", command=win.destroy).pack(pady=16)

# ---------------------- Navigation bar (top) ----------------------
if CTK_AVAILABLE:
    nav_frame = ctk.CTkFrame(app, corner_radius=0)
else:
    nav_frame = Frame(app, bg="")

nav_win = canvas.create_window(screen_w//2, int(screen_h*0.12), window=nav_frame, anchor="n")

def nav_home(): play_click()
def nav_admin(): open_admin_window()
def nav_att(): run_script_nonblocking(ATTENDANCE_SCRIPT)
def nav_student(): run_script_nonblocking(STUDENT_SCRIPT)
def nav_train(): run_script_nonblocking(TRAIN_SCRIPT)

def make_nav_button(parent, text, cmd):
    if CTK_AVAILABLE:
        b = ctk.CTkButton(parent, text=text, width=110, command=cmd)
    else:
        b = Button(parent, text=text, width=12, command=cmd)
    return b

btns = [
    make_nav_button(nav_frame, "Home", nav_home),
    make_nav_button(nav_frame, "Admin", nav_admin),
    make_nav_button(nav_frame, "Attendance", nav_att),
    make_nav_button(nav_frame, "Student", nav_student),
    make_nav_button(nav_frame, "Train", nav_train),
]

for i,b in enumerate(btns):
    if CTK_AVAILABLE:
        b.grid(row=0, column=i, padx=8)
    else:
        b.grid(row=0, column=i, padx=6)

# ---------------------- Main buttons on panel ----------------------
# center-left and center-right positions relative to panel container
btn_user = make_button(container, "User Login (Face)", open_user_window, 0.5, 0.44, icon=user_icon_tk)
btn_admin = make_button(container, "Admin Login (Dashboard)", open_admin_window, 0.5, 0.72, icon=admin_icon_tk)

# ---------------------- Exit info + ESC handling ----------------------
if CTK_AVAILABLE:
    exit_lbl = ctk.CTkLabel(app, text="Press ESC to Exit", font=ctk.CTkFont(size=12))
else:
    exit_lbl = Label(app, text="Press ESC to Exit", font=("Arial", 12), bg="")

canvas.create_window(int(screen_w*0.88), int(screen_h*0.95), window=exit_lbl, anchor="center")

def on_escape(e=None):
    try:
        app.attributes("-fullscreen", False)
    except Exception:
        pass
    app.destroy()

app.bind("<Escape>", on_escape)

# ---------------------- Refresh frosted panel in background ----------------------
def refresh_frost():
    global frost_img
    try:
        frost_img = create_frosted_image(panel_cx, panel_cy, GLASS_WIDTH, GLASS_HEIGHT)
        canvas.itemconfigure(panel_img_id, image=frost_img)
    except Exception:
        pass
    app.after(1500, refresh_frost)

app.after(1500, refresh_frost)

# keep references
canvas.bg_ref = bg_tk if 'bg_tk' in globals() else None
canvas.frost_ref = frost_img

# ---------------------- Run app ----------------------
app.mainloop()
