import json
import os

from flask import Flask, render_template, request, jsonify
from flask import redirect, url_for, session

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


app = Flask(__name__)

app.secret_key = "change_this_secret_key"

USERS_FILE = "users.json"


homework = [
    {
        "title": "Математика",
        "description": "Решить задания по теме квадратных уравнений.",
        "deadline": "18 сентября",
        "image": "math.jpg"
    },
    {
        "title": "Информатика",
        "description": "Создать Flask-приложение с авторизацией.",
        "deadline": "20 сентября",
        "image": "informatics.jpg"
    },
    {
        "title": "Русский язык",
        "description": "Выполнить упражнения по заданной теме.",
        "deadline": "21 сентября",
        "image": "russian.jpg"
    },
    {
        "title": "Английский язык",
        "description": "Выучить новые слова и выполнить упражнения.",
        "deadline": "22 сентября",
        "image": "english.jpg"
    }
]


def load_users():
    if not os.path.exists(USERS_FILE):
        return []

    with open(USERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            users,
            file,
            ensure_ascii=False,
            indent=4
        )


@app.route("/")
def home():

    if "username" in session:
        return redirect(url_for("dashboard"))

    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Заполните все поля"
        }), 400

    if len(username) < 3:
        return jsonify({
            "success": False,
            "message": "Логин должен содержать минимум 3 символа"
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Пароль должен содержать минимум 6 символов"
        }), 400

    users = load_users()

    for user in users:

        if user["username"] == username:

            return jsonify({
                "success": False,
                "message": "Такой пользователь уже существует"
            }), 409

    new_user = {
        "username": username,
        "password": generate_password_hash(password)
    }

    users.append(new_user)

    save_users(users)

    return jsonify({
        "success": True,
        "message": "Аккаунт успешно создан"
    }), 201


@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "")

    users = load_users()

    for user in users:

        if user["username"] == username:

            if check_password_hash(
                user["password"],
                password
            ):

                session["username"] = username

                return jsonify({
                    "success": True,
                    "redirectUrl": url_for("dashboard")
                }), 200

            break

    return jsonify({
        "success": False,
        "message": "Неверный логин или пароль"
    }), 401


@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect(url_for("home"))

    return render_template(
        "dashboard.html",
        username=session["username"],
        homework=homework
    )


@app.route("/maths")
def maths():

    if "username" not in session:
        return redirect(url_for("home"))

    math_homework = [
        item for item in homework
        if item["title"] == "Математика"
    ]

    return render_template(
        "maths.html",
        username=session["username"],
        homework=math_homework
    )


@app.route("/logout")
def logout():

    session.pop("username", None)

    return redirect(url_for("home"))

@app.route("/submit_homework", methods=["POST"])
def submit_homework():
    if "username" not in session:
        return jsonify({
            "success": False,
            "message": "Необходима авторизация"
        }), 401

    homework_text = request.form.get("homework_text", "").strip()
    file = request.files.get("homework_file")

    if not homework_text and not file:
        return jsonify({
            "success": False,
            "message": "Заполните текст решения или прикрепите файл"
        }), 400

    print(f"Пользователь: {session['username']} сдал Домашняя работу, Текст: {homework_text}")
    if file:
        print(f"Прикрепленный файл: {file.filename}")

        return jsonify({
            "success": True,
            "message": "Домашняя работа успешно оправлена"
        }), 200

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )
