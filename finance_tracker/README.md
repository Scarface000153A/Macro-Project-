# FinTrack - Personal Finance & Attendance Tracker

A full-stack, secure, multi-user web application built with **Python (Flask)**, **SQLite**, and **HTML5 / CSS3 / JavaScript**.

---

## Features

- **Multi-User Account Isolation**:
  - Secure User Registration & Login with hashed passwords (`werkzeug.security`).
  - Strict user separation: Every user gets their own fresh dashboard, financial records, and attendance logs. No user can see or modify another user's data.
  - Persistent SQLite database (`finance_tracker.db`): All data is saved permanently across restarts.

- **Personal Finance Management**:
  - **Add Money (Income)**: Record earnings, salary, freelance payouts, etc.
  - **Withdraw Money (Expenses)**: Record expenses with specific categories (Dining, Groceries, Rent, Utilities, etc.).
  - **Automated Real-Time Calculations**:
    - Net Balance = Total Income - Total Expenses
    - Total Money Added
    - Total Money Expensed
    - Savings Percentage Rate %
  - **Interactive Analytics Charts** (Powered by Chart.js):
    - Category Expense Breakdown Doughnut Chart
    - Income vs. Expense Comparison Bar Chart
  - **Search & Filters**: Filter transactions by type (income/expense) or specific categories.
  - **Delete Records**: Easily delete any erroneous transactions with safety confirmation.

- **Attendance Tracker**:
  - Daily quick check-in / check-out with time tracking.
  - Log statuses: `Present`, `Work From Home`, `Half-Day`, `Leave`, `Absent`.
  - Attendance summary analytics & Attendance Percentage (%) calculator.
  - Full historical log of all marked days.

- **Multi-Currency Support**:
  - Switch easily between ₹ (INR), $ (USD), € (EUR), £ (GBP), ¥ (JPY), AED, and more!

---

## How Python Connects to HTML/CSS

```
Browser (User)
      ▲
      │  HTTP Requests (GET, POST) / HTML Pages & JSON
      ▼
Python Flask Web Server (app.py)
   ├── Routing (@app.route('/login'), @app.route('/dashboard'), etc.)
   ├── Authentication & Session Management (session['user_id'])
   ├── Data Processing & Calculations (Balance = Income - Expenses)
   │
   ├── HTML/CSS Rendering (Jinja2 Templates in /templates & /static)
   │     └── templates/login.html, register.html, dashboard.html, attendance.html
   │
   ▼
SQLite Database (finance_tracker.db via database.py)
   ├── users (id, username, email, password_hash, currency)
   ├── transactions (id, user_id, type, amount, category, date)
   └── attendance (id, user_id, date, status, check_in, check_out, notes)
```

---

## How to Run the Website

### Step 1: Open Terminal / Command Prompt
Navigate to the project folder:
```bash
cd C:\Users\User\.gemini\antigravity\scratch\finance_tracker
```

### Step 2: Install Flask (if not already installed)
```bash
pip install -r requirements.txt
```

### Step 3: Start the Application
Run:
```bash
python run.py
```
*(or run `python app.py`)*

### Step 4: Open in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
- Click **"Create Account"** to register your user profile.
- Log in with your new credentials.
- Add income and expenses, or log your attendance!
- When you log out and log in again, your data will always be saved.
- If another person registers an account, their data will be completely separate and start fresh!
