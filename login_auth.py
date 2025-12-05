# --- login_auth.py ---
def check_user_login(username, password):
    # Login for face_rec.py user
    if username == "user" and password == "1234":
        return "USER"
    # Login for admin modules
    elif username == "admin" and password == "admin123":
        return "ADMIN"
    else:
        return None
