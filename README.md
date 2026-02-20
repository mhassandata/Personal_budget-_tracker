# 💰 Personal Budget Tracker

A clean, interactive personal finance dashboard built with **Python** and **Streamlit**. Track your daily expenses, monitor your monthly budget in **Pakistani Rupees (Rs)**, and visualise your spending patterns — all stored locally with no cloud dependency.

---

## 🚀 Features

| Feature | Description |
|---|---|
| ➕ **Add Expenses** | Log expenses with name, category, amount (Rs), and date |
| 📊 **Visual Dashboard** | Pie chart (by category) and bar chart (daily spending) |
| 🎯 **Budget Tracking** | Set a monthly budget and watch a live progress bar |
| 🔍 **Filter & Search** | Filter expenses by category and custom date range |
| ⬇️ **Download Report** | Export filtered expenses to a CSV file instantly |
| 🗑️ **Clear Records** | Safely wipe all records with a confirmation step |
| 💾 **Local Storage** | All data saved in a local SQLite database (`budget.db`) |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **Plotly Express** — Interactive charts
- **Pandas** — Data manipulation
- **SQLite** — Lightweight local database (via Python's built-in `sqlite3`)

---

## 📁 Project Structure

```
budget_tracker/
│
├── app.py           # Main Streamlit application
├── database.py      # All SQLite database operations
├── requirements.txt # Python dependencies
├── budget.db        # Auto-created SQLite database (after first run)
└── README.md        # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/mhassandata/Personal_budget-_tracker.git
cd Personal_budget-_tracker
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**

---

## 📖 How to Use

1. **Set your monthly budget** in the sidebar (Rs amount)
2. **Add an expense** using the form — enter name, category, amount, and date
3. **View your dashboard** — charts update automatically
4. **Filter expenses** by category or date range in the sidebar
5. **Download a report** — click ⬇️ Download Report (CSV) under the Expense History table
6. **Start fresh** — scroll to "Manage Records" at the bottom and use the Clear All Records option

---

## 📦 Expense Categories

`Food` · `Transport` · `Entertainment` · `Bills` · `Shopping` · `Other`

---

## 📋 Requirements

See [`requirements.txt`](requirements.txt) for the full list. Key packages:

```
streamlit
pandas
plotly
```

---

## 🙌 Author

**Muhammad Hassan**  
GitHub: [@mhassandata](https://github.com/mhassandata)
