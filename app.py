# ==============================
# HealthPulse - Flask App (Final Clean)
# ==============================

from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import joblib
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sqlite3
from datetime import date
import random
import smtplib
from reportlab.pdfgen import canvas
from email.mime.text import MIMEText
app = Flask(__name__)
app.secret_key = "healthpulse_secret"
# ML model load
model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")
otp_storage = {}
# =============================
# SQLite Database Connection
# =============================

conn = sqlite3.connect("healthpulse.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (

email TEXT PRIMARY KEY,
password TEXT,
visit_date TEXT,

name TEXT,
age INTEGER,
gender TEXT,
blood_group TEXT,
marital_status TEXT,
phone TEXT,
emergency_contact TEXT,
address TEXT,

height REAL,
weight REAL,
bmi REAL,

department TEXT,
symptoms TEXT,

bp TEXT,
sugar TEXT,
cholesterol TEXT,
heart_rate TEXT,
temperature TEXT,
oxygen TEXT,

smoking TEXT,
alcohol TEXT,
activity TEXT,
diet TEXT,
sleep TEXT,

diabetes TEXT,
hypertension TEXT,
heart_history TEXT,
family_history TEXT,
surgery TEXT,
allergies TEXT,
medication TEXT,

covid_vaccine TEXT,
hepatitis_vaccine TEXT,
flu_vaccine TEXT
)
""")

conn.commit()
def send_otp_email(receiver_email, otp):

    sender_email = "healthpulse132@gmail.com"
    sender_password = "qhbi zhkp unea jftb"

    subject = "HealthPulse OTP Verification"
    body = f"Your OTP for HealthPulse Patient Portal is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)

    server.sendmail(sender_email, receiver_email, msg.as_string())

    server.quit()


# ==============================
# Safe Load Model & Scaler
# ==============================
model = None
scaler = None

if os.path.exists("model.pkl") and os.path.exists("scaler.pkl"):
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
else:
    print("⚠ model.pkl or scaler.pkl not found. Prediction will not work.")


# ==============================
# Home Page
# ==============================
@app.route("/")
def home():
    return render_template("index.html")



# ==============================
# Prediction Page
# ==============================
@app.route("/predict")
def predict():
    return render_template("predict.html")


# ==============================
# Prediction Result
# ==============================
@app.route("/result", methods=["POST"])
def result():

    if model is None or scaler is None:
        return "Model not trained. Please run train_model.py first."

    try:
        input_features = [float(x) for x in request.form.values()]
        final_input = scaler.transform([input_features])
        prediction = model.predict(final_input)

        output = "High Risk of Heart Disease" if prediction[0] == 1 else "Low Risk of Heart Disease"

        return render_template("predict.html", prediction_text=output)

    except Exception as e:
        return f"Prediction Error: {str(e)}"


# ==============================
# Admin Login
# ==============================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            return redirect("/admin-dashboard")
        return "Invalid Admin Credentials"

    return render_template("admin_login.html")


# ==============================
# Doctor Login
# ==============================
@app.route("/doctor-login", methods=["GET", "POST"])
def doctor_login():

    if request.method == "POST":

        username = request.form["username"].strip().lower()
        password = request.form["password"].strip()

        if username == "priya sharma" and password == "priya123":
            return redirect("/doctor-dashboard")

        return "Invalid Doctor Credentials"

    return render_template("doctor_login.html")
##################
#########
###################docotr dashboard
########################
@app.route("/doctor-dashboard")
def doctor_dashboard():

    patients = [
        {"name": "Amit Singh", "age": 45, "condition": "Hypertension", "status": "Stable", "risk": "35%", "date": "2026-02-10"},
        {"name": "Sunita Devi", "age": 62, "condition": "Diabetes Type 2", "status": "Stable", "risk": "48%", "date": "2026-02-08"},
        {"name": "Rajesh Gupta", "age": 38, "condition": "Asthma", "status": "Recovering", "risk": "12%", "date": "2026-02-12"},
        {"name": "Fatima Khan", "age": 55, "condition": "Coronary Artery Disease", "status": "Critical", "risk": "72%", "date": "2026-02-05"},
        {"name": "Vikram Reddy", "age": 29, "condition": "Healthy", "status": "Stable", "risk": "5%", "date": "2026-01-28"},
        {"name": "Lakshmi Iyer", "age": 70, "condition": "COPD", "status": "Critical", "risk": "60%", "date": "2026-02-11"},
    ]

    return render_template("doctor_dashboard.html", patients=patients)


# ==============================
# Patient Login
# ==============================
@app.route("/patient-login", methods=["GET","POST"])
def patient_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("healthpulse.db")
        cursor = conn.cursor()

        cursor.execute(
        "SELECT * FROM patients WHERE email=? AND password=?",
        (email,password)
        )

        patient = cursor.fetchone()

        if patient:

            session["patient_email"] = email

            return redirect("/patient-dashboard")

        else:

            return "Invalid Email or Password"

    return render_template("patient_login.html")
####======================================
#patient dashboard============
#-=========================================
@app.route("/patient-dashboard")
def patient_dashboard():

    if "patient_email" not in session:
        return redirect("/patient-login")

    email = session["patient_email"]

    conn = sqlite3.connect("healthpulse.db")
    cursor = conn.cursor()

    cursor.execute("""
       SELECT name,age,gender,blood_group,phone,bp,sugar,bmi,heart_rate,temperature
      FROM patients
      WHERE email=?
       """,(email,))

    patient = cursor.fetchone()
    conn.close()

    return render_template(
        "patient_dashboard.html",
        patient=patient
    )
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")
#prediction route333333############
#=========================
@app.route("/patient-predictions")
def patient_predictions():

    conn = sqlite3.connect("healthpulse.db")
    cursor = conn.cursor()

    email = session["patient_email"]

    cursor.execute("""
    SELECT age FROM patients
    WHERE email=?
    """, (email,))

    patient = cursor.fetchone()
    age = patient[0]

    cholesterol = 220
    bp = 140
    glucose = 110
    bmi = 27

    features = np.array([[age, cholesterol, bp, glucose, bmi]])

    features_scaled = scaler.transform(features)

    prediction = model.predict_proba(features_scaled)

    heart_risk = int(prediction[0][1] * 100)
    diabetes_risk = int((glucose / 200) * 100)

    today = date.today()
    today_date = today.strftime("%Y-%m-%d")

    conn.close()

    return render_template(
        "patient_predictions.html",
        heart_percent = heart_risk,
        diabetes_percent = diabetes_risk,
        heart_risk = "Moderate Risk",
        diabetes_risk = "Low Risk",
        date = today_date,
        patient_name = "Patient"
    )
@app.route("/download-report")
def download_report():

    email = session["patient_email"]

    filename = "report_"+email+".pdf"

    c = canvas.Canvas(filename)

    c.drawString(100,750,"HealthPulse Health Report")
    c.drawString(100,720,"Patient Email: "+email)

    c.save()

    return send_file(filename, as_attachment=True)
#-=================
#vaccination##############
###############################33
@app.route("/vaccinations")
def vaccinations():

    if "patient_email" not in session:
        return redirect("/patient-login")

    email = session["patient_email"]

    conn = sqlite3.connect("healthpulse.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT covid_vaccine, hepatitis_vaccine, flu_vaccine
    FROM patients
    WHERE email=?
    """,(email,))

    vaccines = cursor.fetchone()

    conn.close()

    return render_template(
        "vaccinations.html",
        vaccines=vaccines
    )
# ==============================
# Admin Dashboard
# ==============================
@app.route("/admin-dashboard")
def admin_dashboard():
    conn = sqlite3.connect("healthpulse.db")
    cursor = conn.cursor()

    # ❗ SAFE QUERY (sirf existing columns use kar rahe)
    cursor.execute("SELECT name, age FROM patients")
    data = cursor.fetchall()

    patients = []
    for i, row in enumerate(data):
        patients.append({
            "id": f"P{str(i+1).zfill(3)}",
            "name": row[0],
            "age": row[1],
            "condition": "General",   # default value
            "status": "Stable"       # default value
        })

    total_patients = len(patients)

    conn.close()

    return render_template(
        "admin_dashboard.html",
        patients=patients,
        total_patients=total_patients
    )
@app.route("/hospital-resources")
def hospital_resources():
    return render_template("hospital_resources.html")

# ==============================
# User Management
# ==============================
@app.route("/user-management")
def user_management():

    doctors = [
        {"id": "D001", "name": "Dr. Priya Sharma", "spec": "Cardiology", "patients": 45, "status": "Active"},
        {"id": "D002", "name": "Dr. Rahul Verma", "spec": "Endocrinology", "patients": 38, "status": "Active"},
        {"id": "D003", "name": "Dr. Anita Desai", "spec": "General Medicine", "patients": 52, "status": "Active"},
        {"id": "D004", "name": "Dr. Suresh Kumar", "spec": "Pulmonology", "patients": 30, "status": "Leave"},
    ]

    patients = [
        {"id": "P001", "name": "Amit Singh", "age": 45, "condition": "Hypertension", "status": "Stable"},
        {"id": "P002", "name": "Sunita Devi", "age": 62, "condition": "Diabetes Type 2", "status": "Stable"},
        {"id": "P003", "name": "Rajesh Gupta", "age": 38, "condition": "Asthma", "status": "Recovering"},
        {"id": "P004", "name": "Fatima Khan", "age": 55, "condition": "Heart Disease", "status": "Critical"},
        {"id": "P005", "name": "Vikram Reddy", "age": 29, "condition": "Healthy", "status": "Stable"},
        {"id": "P006", "name": "Lakshmi Devi", "age": 50, "condition": "Diabetes", "status": "Stable"},
    ]

    return render_template("user_management.html", doctors=doctors, patients=patients)


# ==============================
# Hospital Resources (Dynamic Donut)
# ==============================

#++++++++++++++9696658690
#patient sign in
#========================
#================================
@app.route("/patient-signin")
@app.route("/patient_signin")
def patient_signin():
    return render_template("patient_signin.html")
@app.route("/send-otp", methods=["POST"])
def send_otp():

    email = request.form["email"]

    otp = random.randint(100000,999999)

    otp_storage[email] = otp

    send_otp_email(email, otp)

    return render_template("patient_signin.html", email=email, otp_sent=True)
@app.route("/resend-otp", methods=["POST"])
def resend_otp():

    email = request.form["email"]

    otp = random.randint(100000,999999)

    otp_storage[email] = otp

    send_otp_email(email, otp)

    return render_template("patient_signin.html", email=email, otp_sent=True)
@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    email = request.form["email"]
    user_otp = request.form["otp"]

    if email in otp_storage and str(otp_storage[email]) == user_otp:

        return render_template("patient_register.html", email=email)

    else:

     return  render_template(
        "patient_signin.html",
        email=email,
        otp_sent=True,
        error="Invalid OTP"
        )
    #=======================
    #patient registraion form#
    #========================
@app.route("/register-patient", methods=["POST"])
def register_patient():
    email = request.form["email"]
    password = request.form["password"]
    visit_date = request.form["visit_date"]

    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]
    blood_group = request.form["blood_group"]
    marital_status = request.form["marital_status"]
    phone = request.form["phone"]
    emergency_contact = request.form["emergency_contact"]
    address = request.form["address"]

    height = float(request.form["height"])
    weight = float(request.form["weight"])

    bmi = round(weight / ((height/100)**2),2)

    department = request.form["department"]
    symptoms = request.form["symptoms"]

    bp = request.form["bp"]
    sugar = request.form["sugar"]
    cholesterol = request.form["cholesterol"]
    heart_rate = request.form["heart_rate"]
    temperature = request.form["temperature"]
    oxygen = request.form["oxygen"]

    smoking = request.form["smoking"]
    alcohol = request.form["alcohol"]
    activity = request.form["activity"]
    diet = request.form["diet"]
    sleep = request.form["sleep"]

    diabetes = request.form["diabetes"]
    hypertension = request.form["hypertension"]
    heart_history = request.form["heart_history"]
    family_history = request.form["family_history"]
    surgery = request.form["surgery"]
    allergies = request.form["allergies"]
    medication = request.form["medication"]

    covid_vaccine = request.form["covid_vaccine"]
    hepatitis_vaccine = request.form["hepatitis_vaccine"]
    flu_vaccine = request.form["flu_vaccine"]

    cursor.execute("""

    INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)

    """,(email,password,visit_date,name,age,gender,blood_group,marital_status,phone,
    emergency_contact,address,height,weight,bmi,department,symptoms,bp,sugar,
    cholesterol,heart_rate,temperature,oxygen,smoking,alcohol,activity,diet,sleep,
    diabetes,hypertension,heart_history,family_history,surgery,allergies,medication,
    covid_vaccine,hepatitis_vaccine,flu_vaccine))

    conn.commit()

    return render_template("registration_success.html")
# ==============================
# Run App
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
