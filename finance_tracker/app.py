import os
from functools import wraps
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "finance_tracker_secret_key_2026_secure")

# Ensure database tables exist at startup
init_db()

def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Context processor to inject user details into all templates
@app.context_processor
def inject_user():
    if "user_id" in session:
        return {
            "current_user": {
                "id": session.get("user_id"),
                "username": session.get("username"),
                "full_name": session.get("full_name"),
                "currency": session.get("currency", "₹")
            }
        }
    return {"current_user": None}

# ----------------- AUTHENTICATION ROUTES ----------------- #

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        currency = request.form.get("currency", "₹").strip()

        # Validation
        if not full_name or not username or not email or not password:
            flash("All fields are required!", "danger")
            return render_template("register.html", full_name=full_name, username=username, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html", full_name=full_name, username=username, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", full_name=full_name, username=username, email=email)

        password_hash = generate_password_hash(password)

        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, full_name, password_hash, currency) VALUES (?, ?, ?, ?, ?)",
                    (username, email, full_name, password_hash, currency)
                )
            flash("Registration successful! You can now log in with your account.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            if "UNIQUE constraint failed: users.username" in str(e):
                flash("Username is already taken. Please choose another one.", "danger")
            elif "UNIQUE constraint failed: users.email" in str(e):
                flash("Email is already registered. Please use another email or log in.", "danger")
            else:
                flash(f"Error registering user: {e}", "danger")
            return render_template("register.html", full_name=full_name, username=username, email=email)

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username_or_email = request.form.get("username_or_email", "").strip().lower()
        password = request.form.get("password", "")

        if not username_or_email or not password:
            flash("Please enter both username/email and password.", "danger")
            return render_template("login.html")

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? OR email = ?",
                (username_or_email, username_or_email)
            )
            user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["currency"] = user["currency"] or "₹"
            flash(f"Welcome back, {user['full_name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username/email or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))

# ----------------- DASHBOARD & FINANCE ROUTES ----------------- #

@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    filter_type = request.args.get("type", "all")
    filter_category = request.args.get("category", "all")
    
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Calculate overall totals for the current user
        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = ? AND type = 'income'",
            (user_id,)
        )
        total_income = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = ? AND type = 'expense'",
            (user_id,)
        )
        total_expense = cursor.fetchone()[0]

        balance = total_income - total_expense
        savings_rate = round((balance / total_income * 100), 1) if total_income > 0 else 0

        # 2. Get filtered transactions list
        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [user_id]

        if filter_type in ("income", "expense"):
            query += " AND type = ?"
            params.append(filter_type)
            
        if filter_category and filter_category != "all":
            query += " AND category = ?"
            params.append(filter_category)

        query += " ORDER BY date DESC, id DESC"
        cursor.execute(query, params)
        transactions = cursor.fetchall()

        # 3. Expense category breakdown
        cursor.execute(
            "SELECT category, SUM(amount) as total FROM transactions WHERE user_id = ? AND type = 'expense' GROUP BY category ORDER BY total DESC",
            (user_id,)
        )
        expense_by_category = cursor.fetchall()

        # 4. Income category breakdown
        cursor.execute(
            "SELECT category, SUM(amount) as total FROM transactions WHERE user_id = ? AND type = 'income' GROUP BY category ORDER BY total DESC",
            (user_id,)
        )
        income_by_category = cursor.fetchall()

        # 5. Distinct categories used by user for filter dropdown
        cursor.execute("SELECT DISTINCT category FROM transactions WHERE user_id = ? ORDER BY category", (user_id,))
        available_categories = [row["category"] for row in cursor.fetchall()]

        # 6. Quick attendance snippet
        today_str = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT * FROM attendance WHERE user_id = ? AND date = ?", (user_id, today_str))
        today_attendance = cursor.fetchone()

    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        savings_rate=savings_rate,
        transactions=transactions,
        expense_by_category=expense_by_category,
        income_by_category=income_by_category,
        available_categories=available_categories,
        filter_type=filter_type,
        filter_category=filter_category,
        today_attendance=today_attendance,
        today_date=today_str
    )

@app.route("/transactions/add", methods=["POST"])
@login_required
def add_transaction():
    user_id = session["user_id"]
    t_type = request.form.get("type", "expense").strip().lower()
    amount_str = request.form.get("amount", "0").strip()
    category = request.form.get("category", "General").strip()
    description = request.form.get("description", "").strip()
    date_str = request.form.get("date", "").strip()

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    if t_type not in ("income", "expense"):
        flash("Invalid transaction type selected.", "danger")
        return redirect(url_for("dashboard"))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash("Amount must be greater than zero.", "danger")
            return redirect(url_for("dashboard"))
    except ValueError:
        flash("Invalid amount format.", "danger")
        return redirect(url_for("dashboard"))

    if not category:
        category = "General"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (user_id, type, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, t_type, amount, category, description, date_str)
        )

    flash(f"Successfully added {t_type} of {session.get('currency', '₹')}{amount:.2f}!", "success")
    return redirect(url_for("dashboard"))

@app.route("/transactions/delete/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):
    user_id = session["user_id"]
    with get_db() as conn:
        cursor = conn.cursor()
        # Verify transaction belongs to this user
        cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id))
        if cursor.rowcount > 0:
            flash("Transaction deleted successfully.", "info")
        else:
            flash("Transaction not found or unauthorized.", "danger")

    return redirect(url_for("dashboard"))

# ----------------- ATTENDANCE ROUTES ----------------- #

@app.route("/attendance")
@login_required
def attendance_page():
    user_id = session["user_id"]
    today_str = datetime.now().strftime("%Y-%m-%d")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance WHERE user_id = ? ORDER BY date DESC", (user_id,))
        records = cursor.fetchall()

        # Compute attendance stats
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE user_id = ?", (user_id,))
        total_days = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE user_id = ? AND status IN ('Present', 'Work From Home')",
            (user_id,)
        )
        present_days = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE user_id = ? AND status = 'Absent'",
            (user_id,)
        )
        absent_days = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM attendance WHERE user_id = ? AND status IN ('Leave', 'Half-Day')",
            (user_id,)
        )
        leave_days = cursor.fetchone()[0]

        attendance_pct = round((present_days / total_days * 100), 1) if total_days > 0 else 0

        # Today's status if marked
        cursor.execute("SELECT * FROM attendance WHERE user_id = ? AND date = ?", (user_id, today_str))
        today_record = cursor.fetchone()

    return render_template(
        "attendance.html",
        records=records,
        total_days=total_days,
        present_days=present_days,
        absent_days=absent_days,
        leave_days=leave_days,
        attendance_pct=attendance_pct,
        today_record=today_record,
        today_date=today_str
    )

@app.route("/attendance/mark", methods=["POST"])
@login_required
def mark_attendance():
    user_id = session["user_id"]
    date_str = request.form.get("date", "").strip()
    status = request.form.get("status", "Present").strip()
    check_in = request.form.get("check_in", "").strip()
    check_out = request.form.get("check_out", "").strip()
    notes = request.form.get("notes", "").strip()

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    valid_statuses = ("Present", "Absent", "Half-Day", "Leave", "Work From Home")
    if status not in valid_statuses:
        flash("Invalid attendance status.", "danger")
        return redirect(url_for("attendance_page"))

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO attendance (user_id, date, status, check_in, check_out, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
                status = excluded.status,
                check_in = excluded.check_in,
                check_out = excluded.check_out,
                notes = excluded.notes
            """,
            (user_id, date_str, status, check_in, check_out, notes)
        )

    flash(f"Attendance for {date_str} marked as '{status}' successfully!", "success")
    return redirect(url_for("attendance_page"))

@app.route("/attendance/delete/<int:record_id>", methods=["POST"])
@login_required
def delete_attendance(record_id):
    user_id = session["user_id"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance WHERE id = ? AND user_id = ?", (record_id, user_id))
        if cursor.rowcount > 0:
            flash("Attendance record deleted.", "info")
        else:
            flash("Record not found or unauthorized.", "danger")

    return redirect(url_for("attendance_page"))

# ----------------- SETTINGS & API ROUTES ----------------- #

@app.route("/settings/currency", methods=["POST"])
@login_required
def update_currency():
    user_id = session["user_id"]
    currency = request.form.get("currency", "₹").strip()
    if currency:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET currency = ? WHERE id = ?", (currency, user_id))
        session["currency"] = currency
        flash(f"Preferred currency updated to {currency}", "success")
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/api/chart-data")
@login_required
def chart_data():
    """Returns JSON breakdown data for Chart.js"""
    user_id = session["user_id"]
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Expense by category
        cursor.execute(
            "SELECT category, SUM(amount) as total FROM transactions WHERE user_id = ? AND type = 'expense' GROUP BY category",
            (user_id,)
        )
        expense_cats = [{"category": row["category"], "total": row["total"]} for row in cursor.fetchall()]

        # Income by category
        cursor.execute(
            "SELECT category, SUM(amount) as total FROM transactions WHERE user_id = ? AND type = 'income' GROUP BY category",
            (user_id,)
        )
        income_cats = [{"category": row["category"], "total": row["total"]} for row in cursor.fetchall()]

    return jsonify({
        "expense": expense_cats,
        "income": income_cats
    })

if __name__ == "__main__":
    print("Starting Personal Finance & Attendance Tracker...")
    print("Open your browser and navigate to: http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
