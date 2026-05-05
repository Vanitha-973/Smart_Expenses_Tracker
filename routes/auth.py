from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models.db import execute_db, query_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/title")
def title_screen():
    if session.get("user_id"):
        return redirect(url_for("analytics.dashboard"))
    return render_template("title.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("analytics.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        existing_user = query_db(
            "SELECT id, username, email FROM users WHERE username = %s OR email = %s",
            (username, email),
            one=True,
        )
        if existing_user:
            flash("Username or email already exists.", "danger")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        execute_db(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash),
        )
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("analytics.dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")

        user = query_db(
            "SELECT id, username, email, password_hash FROM users WHERE username = %s OR email = %s",
            (identifier, identifier),
            one=True,
        )

        if not user or "password_hash" not in user or not check_password_hash(user["password_hash"], password):
            flash("Invalid login details.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("Logged in successfully.", "success")
        return redirect(url_for("analytics.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
