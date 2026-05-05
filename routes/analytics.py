from flask import Blueprint, jsonify, render_template, request, session

from decorators import login_required
from models.db import query_db

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]

    totals = query_db(
        "SELECT COALESCE(SUM(amount), 0) AS total_spent FROM expenses WHERE user_id = %s",
        (user_id,),
        one=True,
    )
    week_total = query_db(
        """
        SELECT COALESCE(SUM(amount), 0) AS total_spent
        FROM expenses
        WHERE user_id = %s AND expense_date >= CURDATE() - INTERVAL 6 DAY
        """,
        (user_id,),
        one=True,
    )
    weekly_daily = query_db(
        """
        SELECT DATE(expense_date) AS day, COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = %s AND expense_date >= CURDATE() - INTERVAL 6 DAY
        GROUP BY DATE(expense_date)
        ORDER BY day
        """,
        (user_id,),
    )
    weekly_categories = query_db(
        """
        SELECT category, COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = %s AND expense_date >= CURDATE() - INTERVAL 6 DAY
        GROUP BY category
        ORDER BY total DESC
        """,
        (user_id,),
    )
    recent_expenses = query_db(
        """
        SELECT id, title, amount, category, expense_date
        FROM expenses
        WHERE user_id = %s
        ORDER BY expense_date DESC, id DESC
        LIMIT 5
        """,
        (user_id,),
    )

    return render_template(
        "dashboard.html",
        total_spent=totals["total_spent"] if totals else 0,
        week_total=week_total["total_spent"] if week_total else 0,
        weekly_daily=weekly_daily,
        weekly_categories=weekly_categories,
        recent_expenses=recent_expenses,
    )


@analytics_bp.route("/last-7-days")
@login_required
def last_7_days():
    return dashboard()


@analytics_bp.route("/monthly-summary")
@login_required
def monthly_summary():
    user_id = session["user_id"]
    selected_month = request.args.get("month")

    months = query_db(
        """
        SELECT DATE_FORMAT(MIN(expense_date), '%Y-%m') AS month_key,
               CONCAT(MONTHNAME(MIN(expense_date)), ' ', YEAR(MIN(expense_date))) AS month_label,
               COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = %s
        GROUP BY YEAR(expense_date), MONTH(expense_date)
        ORDER BY YEAR(expense_date) DESC, MONTH(expense_date) DESC
        """,
        (user_id,),
    )

    if not selected_month and months:
        selected_month = months[0]["month_key"]

    for month in months:
        month["selected_attr"] = "selected" if month["month_key"] == selected_month else ""

    daily_rows = []
    month_total = 0
    if selected_month:
        daily_rows = query_db(
            """
            SELECT DATE(expense_date) AS day, COALESCE(SUM(amount), 0) AS total
            FROM expenses
            WHERE user_id = %s AND DATE_FORMAT(expense_date, '%Y-%m') = %s
            GROUP BY DATE(expense_date)
            ORDER BY day
            """,
            (user_id, selected_month),
        )
        month_total_row = query_db(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM expenses
            WHERE user_id = %s AND DATE_FORMAT(expense_date, '%Y-%m') = %s
            """,
            (user_id, selected_month),
            one=True,
        )
        month_total = month_total_row["total"] if month_total_row else 0

    return render_template(
        "monthly.html",
        months=months,
        selected_month=selected_month,
        daily_rows=daily_rows,
        month_total=month_total,
    )


@analytics_bp.route("/chart-data")
@login_required
def chart_data():
    user_id = session["user_id"]
    daily = query_db(
        """
        SELECT DATE_FORMAT(day_bucket, '%d %b') AS label, COALESCE(total, 0) AS total
        FROM (
            SELECT DATE(expense_date) AS day_bucket, SUM(amount) AS total
            FROM expenses
            WHERE user_id = %s AND expense_date >= CURDATE() - INTERVAL 6 DAY
            GROUP BY DATE(expense_date)
        ) AS data
        RIGHT JOIN (
            SELECT CURDATE() - INTERVAL 6 DAY AS day_bucket
            UNION ALL SELECT CURDATE() - INTERVAL 5 DAY
            UNION ALL SELECT CURDATE() - INTERVAL 4 DAY
            UNION ALL SELECT CURDATE() - INTERVAL 3 DAY
            UNION ALL SELECT CURDATE() - INTERVAL 2 DAY
            UNION ALL SELECT CURDATE() - INTERVAL 1 DAY
            UNION ALL SELECT CURDATE()
        ) AS dates USING (day_bucket)
        ORDER BY day_bucket
        """,
        (user_id,),
    )
    categories = query_db(
        """
        SELECT category AS label, SUM(amount) AS total
        FROM expenses
        WHERE user_id = %s
        GROUP BY category
        ORDER BY total DESC
        """,
        (user_id,),
    )
    monthly = query_db(
        """
        SELECT CONCAT(MONTHNAME(MIN(expense_date)), ' ', YEAR(MIN(expense_date))) AS label, SUM(amount) AS total
        FROM expenses
        WHERE user_id = %s
        GROUP BY YEAR(expense_date), MONTH(expense_date)
        ORDER BY YEAR(expense_date) DESC, MONTH(expense_date) DESC
        """,
        (user_id,),
    )
    return jsonify(
        {
            "daily_labels": [row["label"] for row in daily],
            "daily_totals": [float(row["total"]) for row in daily],
            "category_labels": [row["label"] for row in categories],
            "category_totals": [float(row["total"]) for row in categories],
            "monthly_labels": [row["label"] for row in monthly],
            "monthly_totals": [float(row["total"]) for row in monthly],
        }
    )
