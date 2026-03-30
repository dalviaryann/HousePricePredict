from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import joblib
import sqlite3
import pandas as pd
import os
from jinja2 import pass_context

app = Flask(__name__)
app.jinja_env.globals.update(enumerate=enumerate)
app.secret_key = "mumbai_house_secret_123"

model = joblib.load("model_rf.pkl")
metadata = joblib.load("metadata.pkl")


#database 

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bhk INTEGER,
            area INTEGER,
            property_type TEXT,
            region TEXT,
            status TEXT,
            age TEXT,
            predicted_price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

#throw to sign/login

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

#get post, correct email, same email trigger, logout kick

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid email or password"
    
    return render_template("login.html", error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                         (name, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            error = "Email already exists"
            conn.close()
    
    return render_template("signup.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#ensures only logged in users can acces , and numpy pandas for data for correct form

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    prediction = None
    if request.method == "POST":
        bhk = int(request.form["bhk"])
        area = int(request.form["area"])
        property_type = request.form["type"]
        region = request.form["region"]
        status = request.form["status"]
        age = request.form["age"]
        input_df = pd.DataFrame([{
            "bhk": bhk, "area": area, "type": property_type,
            "region": region, "status": status, "age": age,
        }])
        predicted = float(model.predict(input_df)[0])
        predicted = max(predicted, 0)
        if predicted >= 100:
            prediction = f"₹{predicted/100:.2f} Cr"
        else:
            prediction = f"₹{predicted:.2f} L"
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO searches 
            (user_id, bhk, area, property_type, region, status, age, predicted_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session["user_id"], bhk, area, property_type, region, status, age, predicted))
        conn.commit()
        conn.close()
    return render_template("dashboard.html",
        prediction=prediction,
        metadata=metadata,
        user_name=session["user_name"],
        show_nav=True
    )

@app.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    results = None
    if request.method == "POST":
        bhk = int(request.form["bhk"])
        area = int(request.form["area"])
        budget = float(request.form["budget"])
        status = request.form["status"]
        age = request.form["age"]
        results = []
        for region in metadata["regions"]:
            input_df = pd.DataFrame([{
                "bhk": bhk, "area": area, "type": "Apartment",
                "region": region, "status": status, "age": age,
            }])
            predicted = float(model.predict(input_df)[0])
            if predicted <= budget:
                results.append({
                    "region": region,
                    "predicted": predicted,
                    "formatted": f"₹{predicted/100:.2f} Cr" if predicted >= 100 else f"₹{predicted:.2f} L",
                    "bhk": bhk,
                    "area": area
                })
        results = sorted(results, key=lambda x: x["predicted"])[:6]
    return render_template("compare.html",
        results=results,
        metadata=metadata,
        user_name=session["user_name"],
        show_nav=True
    )

@app.route("/optimizer", methods=["GET", "POST"])
@login_required
def optimizer():
    results = None
    if request.method == "POST":
        budget = float(request.form["budget"])
        bhk = int(request.form["bhk"])
        results = []
        for region in metadata["regions"]:
            input_df = pd.DataFrame([{
                "bhk": bhk, "area": 700, "type": "Apartment",
                "region": region, "status": "Ready to move", "age": "New",
            }])
            predicted = float(model.predict(input_df)[0])
            if predicted <= budget:
                area_you_get = int((budget / predicted) * 700)
                results.append({
                    "region": region,
                    "predicted": predicted,
                    "area_you_get": area_you_get,
                    "formatted": f"₹{predicted/100:.2f} Cr" if predicted >= 100 else f"₹{predicted:.2f} L"
                })
        results = sorted(results, key=lambda x: x["area_you_get"], reverse=True)[:6]
    return render_template("optimizer.html",
        results=results,
        metadata=metadata,
        user_name=session["user_name"],
        show_nav=True
    )

@app.route("/history")
@login_required
def history():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT bhk, area, property_type, region, status, age, predicted_price, created_at 
        FROM searches WHERE user_id=? 
        ORDER BY created_at DESC
    """, (session["user_id"],))
    searches = cursor.fetchall()
    conn.close()
    return render_template("history.html",
        searches=searches,
        user_name=session["user_name"],
        show_nav=True
    )

@app.route("/about")
@login_required
def about():
    return render_template("about.html",
        user_name=session["user_name"],
        show_nav=True
    )

if __name__ == "__main__":
    app.run(debug=True)