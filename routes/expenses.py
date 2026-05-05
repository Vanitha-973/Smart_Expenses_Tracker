from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from decorators import login_required
from models.db import execute_db, query_db

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/view-expenses")
@login_required
def view_expenses():
    expenses = query_db(
        """
        SELECT id, title, amount, category, expense_date, description
        FROM expenses
        WHERE user_id = %s
        ORDER BY expense_date DESC, id DESC
        """,
        (session["user_id"],),
    )
    return render_template("expenses.html", expenses=expenses)


@expenses_bp.route("/add-expense", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        expense_date = request.form.get("expense_date", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not amount or not category or not expense_date:
            flash("Title, amount, category, and date are required.", "danger")
            return render_template("add_expense.html")

        execute_db(
            """
            INSERT INTO expenses (user_id, title, amount, category, expense_date, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (session["user_id"], title, amount, category, expense_date, description or None),
        )
        flash("Expense added.", "success")
        return redirect(url_for("expenses.view_expenses"))

    return render_template("add_expense.html")


@expenses_bp.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    expense = query_db(
        "SELECT * FROM expenses WHERE id = %s AND user_id = %s",
        (expense_id, session["user_id"]),
        one=True,
    )
    if not expense:
        flash("Expense not found.", "warning")
        return redirect(url_for("expenses.view_expenses"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        expense_date = request.form.get("expense_date", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not amount or not category or not expense_date:
            flash("Title, amount, category, and date are required.", "danger")
            return render_template("edit_expense.html", expense=expense)

        execute_db(
            """
            UPDATE expenses
            SET title = %s, amount = %s, category = %s, expense_date = %s, description = %s
            WHERE id = %s AND user_id = %s
            """,
            (title, amount, category, expense_date, description or None, expense_id, session["user_id"]),
        )
        flash("Expense updated.", "success")
        return redirect(url_for("expenses.view_expenses"))

    return render_template("edit_expense.html", expense=expense)


@expenses_bp.route("/delete-expense/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    execute_db(
        "DELETE FROM expenses WHERE id = %s AND user_id = %s",
        (expense_id, session["user_id"]),
    )
    flash("Expense deleted.", "info")
    return redirect(url_for("expenses.view_expenses"))
