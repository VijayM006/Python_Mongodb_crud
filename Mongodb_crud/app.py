from flask import Flask, render_template, request, redirect, url_for,session
from pymongo import MongoClient
import re
from bson.objectid import ObjectId

vj = Flask(__name__)

vj.secret_key="Vijay@006"
mongo_url = "mongodb://localhost:27017/"
client = MongoClient(mongo_url)
db = client.student_details
collection = db.signup

def is_logged_in():
    return "Username" in session

def is_password_strong(Password):
    if len(Password) < 8:
        return False
    if not re.search(r"[a-z]", Password) or not re.search(r"[A-Z]", Password):
        return False
    if not re.search(r"[!@#$%^&*()_+-]", Password):
        return False
    return True

@vj.route("/", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        Username = request.form.get("Username")
        Password = request.form.get("Password")
        Age = request.form.get("Age")
        Email = request.form.get("Email")
        user_dict = {"Username": Username, "Password": Password, "Age": Age, "Email": Email}

        if collection.find_one({"Username": Username}):
            return "Username already exists"
        elif collection.find_one({"Email": Email}):
            return "Email is already taken by another user"
        else:
            if not is_password_strong(Password):
                return "Password is not strong enough"

            collection.insert_one(user_dict)
            return redirect(url_for('login'))

    return render_template("signup.html")

@vj.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        Username = request.form.get("Username")
        Password = request.form.get("Password")

        user = collection.find_one({"Username": Username})

        if user and user["Password"] == Password:
            session["Username"] = Username  # Set the username in session
            return redirect(url_for("home"))
        else:
            return "User details not found. Please sign up."

    return render_template("login.html")

@vj.route("/home")
def home():
    data = []
    if is_logged_in():
        Username = session["Username"]
        data = list(collection.find({"Username": Username}))
    return render_template("index.html", data=data)
@vj.route("/edit/<string:id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "POST":
        Username = request.form.get("Username")
        Password = request.form.get("Password")
        Age = request.form.get("Age")
        Email = request.form.get("Email")

        collection.update_one(
            {"id": ObjectId(id)},
            {"$set": {"Username": Username, "Password": Password, "Age": Age, "Email": Email}}
        )
        return redirect(url_for("home"))

    user = collection.find_one({"_id": ObjectId(id)})
    return render_template("edit.html", user=user)

if __name__ == "__main__":
    vj.run(debug=True, port=1007)
