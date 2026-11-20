import os
import sqlite3
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deployment")
DB_PATH = os.environ.get("DATABASE_PATH", "salon.db")

SALON = {
    "name": "The Premium Studio Unisex Salon",
    "phone": "086006 93862",
    "whatsapp": "918600693862",
    "address": "Shop no 2, Oasis Life Society, Near Indira Nagar Church, In front of Nashik Cambridge School, Nashik, Maharashtra 422009",
    "maps": "https://maps.app.goo.gl/VkjwzVc25JaYcrHH7?g_st=ac",
}
HOURS = {
    0: ("09:00", "22:00"), 1: ("09:00", "22:00"), 2: ("09:00", "22:00"),
    3: ("09:00", "22:00"), 4: ("09:00", "22:00"),
    5: ("08:00", "22:00"), 6: ("08:00", "22:30")
}
SERVICES = [
    "Eyebrow Beautification", "Eyelashes", "Skin Care", "Pedicure",
    "Facial", "Haircut", "Blow Dry", "Body Waxing", "Massage",
    "Makeup", "Manicure", "Hair Styling"
]

def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL
        )""")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_booking_per_exact_slot ON bookings (appointment_date, appointment_time)")
        db.execute("""CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )""")
        if db.execute("SELECT COUNT(*) FROM admins").fetchone()[0] == 0:
            username = os.environ.get("ADMIN_USERNAME", "admin")
            password = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
            db.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                       (username, generate_password_hash(password)))

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

def is_within_hours(day_string, time_string):
    try:
        chosen_date = date.fromisoformat(day_string)
        chosen_time = datetime.strptime(time_string, "%H:%M").time()
    except ValueError:
        return False
    start, end = HOURS[chosen_date.weekday()]
    return datetime.strptime(start, "%H:%M").time() <= chosen_time <= datetime.strptime(end, "%H:%M").time()

@app.route("/")
def home():
    return render_template("index.html", salon=SALON, services=SERVICES, hours=HOURS)

@app.route("/book", methods=["POST"])
def book():
    name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    service = request.form.get("service", "")
    day = request.form.get("appointment_date", "")
    time = request.form.get("appointment_time", "")
    if not name or not phone or service not in SERVICES or not day or not time:
        flash("Please complete every booking field.", "error")
        return redirect(url_for("home") + "#booking")
    if not phone.replace("+", "").replace(" ", "").replace("-", "").isdigit():
        flash("Please enter a valid contact number.", "error")
        return redirect(url_for("home") + "#booking")
    if day < date.today().isoformat() or not is_within_hours(day, time):
        flash("Please choose a future date and a time within the salon opening hours.", "error")
        return redirect(url_for("home") + "#booking")
    try:
        with connect() as db:
            db.execute("""INSERT INTO bookings
                (customer_name, phone, service, appointment_date, appointment_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (name, phone, service, day, time, datetime.now().isoformat(timespec="seconds")))
    except sqlite3.IntegrityError:
        flash("That appointment time has just been booked. Please choose another time.", "error")
        return redirect(url_for("home") + "#booking")
    flash("Your booking request has been received. The salon will contact you to confirm it.", "success")
    return redirect(url_for("home") + "#booking")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with connect() as db:
            admin = db.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("login.html", salon=SALON)

@app.route("/admin")
@admin_required
def dashboard():
    with connect() as db:
        bookings = db.execute("SELECT * FROM bookings ORDER BY appointment_date DESC, appointment_time DESC").fetchall()
    return render_template("dashboard.html", salon=SALON, bookings=bookings)

@app.route("/admin/booking/<int:booking_id>/<action>", methods=["POST"])
@admin_required
def update_booking(booking_id, action):
    statuses = {"confirm": "Confirmed", "reject": "Rejected", "complete": "Completed"}
    if action not in statuses:
        abort(404)
    with connect() as db:
        db.execute("UPDATE bookings SET status = ? WHERE id = ?", (statuses[action], booking_id))
    flash("Booking status updated.", "success")
    return redirect(url_for("dashboard"))

@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}

init_db()

if __name__ == "__main__":
    app.run(debug=True)
