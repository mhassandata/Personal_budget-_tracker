"""
database.py — All SQLite database operations for the Budget Tracker.
The database file (budget.db) is created automatically in this folder.
"""

import sqlite3
import os
from datetime import date, timedelta

# Path to the database file — lives in the same folder as this script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "budget.db")


def _connect():
    """Open a connection and return rows as dictionaries."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─────────────────────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────────────────────

def initialize_db():
    """Create tables if they don't exist and seed default settings."""
    conn = _connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            category TEXT    NOT NULL,
            amount   REAL    NOT NULL,
            date     TEXT    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Default monthly budget of $2,000 — only inserted once
    cur.execute("""
        INSERT OR IGNORE INTO settings (key, value)
        VALUES ('monthly_budget', '2000')
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Expenses
# ─────────────────────────────────────────────────────────────────────────────

def add_expense(name: str, category: str, amount: float, date_str: str = None):
    """Insert a new expense row."""
    if date_str is None:
        date_str = date.today().isoformat()
    conn = _connect()
    conn.execute(
        "INSERT INTO expenses (name, category, amount, date) VALUES (?, ?, ?, ?)",
        (name, category, round(amount, 2), date_str),
    )
    conn.commit()
    conn.close()


def get_expenses_filtered(category: str = None, start_date: str = None, end_date: str = None):
    """Return expenses matching optional category and date-range filters."""
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date DESC, id DESC"

    conn = _connect()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_expenses(year: int, month: int):
    """Return all expenses for a given year-month."""
    month_prefix = f"{year}-{month:02d}"
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM expenses WHERE date LIKE ? ORDER BY date, id",
        (f"{month_prefix}%",),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_expense(expense_id: int):
    """Remove an expense by its id."""
    conn = _connect()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def clear_all_expenses():
    """Delete every row from the expenses table."""
    conn = _connect()
    conn.execute("DELETE FROM expenses")
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Settings
# ─────────────────────────────────────────────────────────────────────────────

def get_monthly_budget() -> float:
    """Return the stored monthly budget amount."""
    conn = _connect()
    row = conn.execute(
        "SELECT value FROM settings WHERE key = 'monthly_budget'"
    ).fetchone()
    conn.close()
    return float(row["value"]) if row else 2000.0


def set_monthly_budget(amount: float):
    """Save the monthly budget amount."""
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES ('monthly_budget', ?)",
        (str(round(amount, 2)),),
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Sample Data
# ─────────────────────────────────────────────────────────────────────────────

def has_any_data() -> bool:
    """Return True if the expenses table already has rows."""
    conn = _connect()
    row = conn.execute("SELECT COUNT(*) AS n FROM expenses").fetchone()
    conn.close()
    return row["n"] > 0


def insert_sample_data():
    """
    Populate the database with realistic sample expenses spread across
    the current month so the charts look interesting on first launch.
    """
    today = date.today()
    days_available = today.day  # how many days have passed this month

    # (name, category, amount)
    samples = [
        ("Grocery store",         "Food",          78.50),
        ("Uber ride",             "Transport",     14.20),
        ("Netflix subscription",  "Entertainment", 15.99),
        ("Electric bill",         "Bills",        118.00),
        ("Morning coffee",        "Food",           4.75),
        ("Amazon purchase",       "Shopping",      52.99),
        ("Lunch with colleague",  "Food",          16.50),
        ("Gym membership",        "Bills",         35.00),
        ("Movie night",           "Entertainment", 28.00),
        ("Gas station",           "Transport",     58.00),
        ("Restaurant dinner",     "Food",          67.00),
        ("Phone bill",            "Bills",         72.00),
        ("Grocery run",           "Food",          45.20),
        ("Monthly bus pass",      "Transport",     30.00),
        ("New sneakers",          "Shopping",      89.99),
        ("Coffee shop",           "Food",           5.50),
        ("Spotify",               "Entertainment",  9.99),
        ("Breakfast cafe",        "Food",          11.00),
        ("Parking meter",         "Transport",      6.00),
        ("Miscellaneous",         "Other",         22.50),
    ]

    conn = _connect()
    for i, (name, category, amount) in enumerate(samples):
        # Spread evenly across days 1 … today (wraps if fewer days than samples)
        day_num = (i % days_available) + 1
        expense_date = today.replace(day=day_num)
        conn.execute(
            "INSERT INTO expenses (name, category, amount, date) VALUES (?, ?, ?, ?)",
            (name, category, amount, expense_date.isoformat()),
        )
    conn.commit()
    conn.close()
