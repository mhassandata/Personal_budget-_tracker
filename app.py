"""
app.py — Personal Budget Tracker
Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

import database as db

# ─────────────────────────────────────────────────────────────────────────────
# Page configuration  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="💰 Budget Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Global CSS tweaks
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Tighten top padding */
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

    /* Form card look */
    section[data-testid="stForm"] {
        background: #f7f9fc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.4rem 1.6rem 1rem 1.6rem;
    }

    /* Slightly larger metric labels */
    [data-testid="stMetricLabel"] p { font-size: 0.95rem !important; }

    /* Category badge colours in the table */
    .badge-Food            { background:#fff3cd; color:#856404;  }
    .badge-Transport       { background:#cfe2ff; color:#084298;  }
    .badge-Entertainment   { background:#e2d9f3; color:#432874;  }
    .badge-Bills           { background:#f8d7da; color:#842029;  }
    .badge-Shopping        { background:#d1e7dd; color:#0a3622;  }
    .badge-Other           { background:#e2e3e5; color:#383d41;  }
    </style>
    """,
    unsafe_allow_html=True,
)

CATEGORIES = ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"]

CATEGORY_COLORS = {
    "Food":          "#FBBF24",
    "Transport":     "#60A5FA",
    "Entertainment": "#A78BFA",
    "Bills":         "#F87171",
    "Shopping":      "#34D399",
    "Other":         "#9CA3AF",
}

# ─────────────────────────────────────────────────────────────────────────────
# One-time setup
# ─────────────────────────────────────────────────────────────────────────────
db.initialize_db()

first_run = not db.has_any_data()
if first_run:
    db.insert_sample_data()

# ─────────────────────────────────────────────────────────────────────────────
# ░░  SIDEBAR — Filters & Budget Settings
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗂️ Filters & Settings")
    st.markdown("---")

    # ── Category filter ───────────────────────────────────────────────────────
    st.markdown("### 🔍 Filter Expenses")
    selected_category = st.selectbox(
        "Category",
        ["All"] + CATEGORIES,
        label_visibility="collapsed",
    )

    # ── Date-range filter ─────────────────────────────────────────────────────
    today = date.today()
    first_of_month = today.replace(day=1)

    start_date = st.date_input("From", value=first_of_month)
    end_date   = st.date_input("To",   value=today)

    if start_date > end_date:
        st.warning("⚠️ 'From' date is after 'To' date.")

    st.markdown("---")

    # ── Budget settings ───────────────────────────────────────────────────────
    st.markdown("### ⚙️ Monthly Budget")
    current_budget = db.get_monthly_budget()
    new_budget = st.number_input(
        "Budget limit (Rs)",
        min_value=0.0,
        value=float(current_budget),
        step=100.0,
        format="%.2f",
    )

    if st.button("💾 Save Budget", use_container_width=True):
        db.set_monthly_budget(new_budget)
        st.success("✅ Budget saved!")
        st.rerun()

    st.markdown("---")
    st.caption("💡 Tip: Use filters above to drill into specific spending.")

# ─────────────────────────────────────────────────────────────────────────────
# ░░  Load data for the current month
# ─────────────────────────────────────────────────────────────────────────────
now = datetime.now()
monthly_rows = db.get_monthly_expenses(now.year, now.month)

if monthly_rows:
    monthly_df = pd.DataFrame(monthly_rows)
else:
    monthly_df = pd.DataFrame(columns=["id", "name", "category", "amount", "date"])

monthly_budget = db.get_monthly_budget()
monthly_total  = float(monthly_df["amount"].sum()) if not monthly_df.empty else 0.0
remaining      = monthly_budget - monthly_total

# ─────────────────────────────────────────────────────────────────────────────
# ░░  HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("# 💰 Personal Budget Tracker")
st.caption(f"📅 {now.strftime('%B %Y')}  ·  Tracking your money so you don't have to worry about it")
st.markdown("---")

if first_run:
    st.info(
        "👋 **Welcome!** We've loaded some sample expenses so you can see "
        "how everything looks. Feel free to delete them and add your own!",
        icon="🎉",
    )

# ─────────────────────────────────────────────────────────────────────────────
# ░░  KEY METRICS
# ─────────────────────────────────────────────────────────────────────────────
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric(
        label="💸 Spent This Month",
        value=f"Rs {monthly_total:,.2f}",
    )

with col_b:
    st.metric(
        label="🎯 Monthly Budget",
        value=f"Rs {monthly_budget:,.2f}",
    )

with col_c:
    delta_label = f"Rs {abs(remaining):,.2f} {'left' if remaining >= 0 else 'OVER budget'}"
    st.metric(
        label="💵 Remaining",
        value=f"Rs {remaining:,.2f}",
        delta=delta_label,
        delta_color="normal" if remaining >= 0 else "inverse",
    )

# ─────────────────────────────────────────────────────────────────────────────
# ░░  BUDGET PROGRESS BAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 📊 Budget Progress")

if monthly_budget > 0:
    pct        = monthly_total / monthly_budget
    pct_capped = min(pct, 1.0)          # cap bar width at 100 %
    pct_label  = pct * 100

    if pct >= 1.0:
        bar_color   = "#EF4444"          # red  — over budget
        status_icon = "🚨"
        status_text = f"Over budget by Rs {monthly_total - monthly_budget:,.2f}!"
    elif pct >= 0.8:
        bar_color   = "#F59E0B"          # amber — warning
        status_icon = "⚠️"
        status_text = f"{pct_label:.1f}% of budget used — getting close!"
    else:
        bar_color   = "#10B981"          # green — all good
        status_icon = "✅"
        status_text = f"{pct_label:.1f}% of budget used — looking good!"

    st.markdown(
        f"""
        <div style="
            background:#E5E7EB;
            border-radius:12px;
            height:32px;
            width:100%;
            overflow:hidden;
            margin-bottom:6px;
        ">
            <div style="
                background:{bar_color};
                width:{pct_capped * 100:.2f}%;
                height:32px;
                border-radius:12px;
                transition:width 0.4s ease;
            "></div>
        </div>
        <p style="
            text-align:center;
            font-weight:600;
            font-size:0.95rem;
            color:{bar_color};
            margin-top:4px;
        ">{status_icon} {status_text}</p>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("Set your monthly budget in the sidebar ← to track your progress here.")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ░░  ADD EXPENSE FORM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## ➕ Add New Expense")

with st.form("expense_form", clear_on_submit=True):
    f1, f2, f3, f4 = st.columns([3, 2, 2, 2])

    with f1:
        exp_name = st.text_input(
            "Expense Name",
            placeholder="e.g. Coffee, Groceries, Uber …",
        )
    with f2:
        exp_category = st.selectbox("Category", CATEGORIES)
    with f3:
        exp_amount = st.number_input(
            "Amount (Rs)",
            min_value=0.0,
            value=0.0,
            step=0.01,
            format="%.2f",
        )
    with f4:
        exp_date = st.date_input("Date", value=date.today())

    submitted = st.form_submit_button("💸 Add Expense", use_container_width=True)

    if submitted:
        name_clean = exp_name.strip()
        if not name_clean:
            st.error("❌ Please enter a name for the expense.")
        elif exp_amount <= 0:
            st.error("❌ Amount must be greater than Rs 0.00.")
        else:
            db.add_expense(name_clean, exp_category, exp_amount, exp_date.isoformat())
            st.success(
                f"✅ **{name_clean}** — Rs {exp_amount:.2f} added to **{exp_category}**!"
            )
            st.rerun()

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ░░  CHARTS DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## 📈 Dashboard")

if monthly_df.empty:
    st.info("No expenses this month yet — add your first one above! ☝️")
else:
    chart_left, chart_right = st.columns(2)

    # ── Pie chart: spending by category ──────────────────────────────────────
    with chart_left:
        st.markdown("#### 🥧 Spending by Category")

        cat_totals = (
            monthly_df.groupby("category")["amount"]
            .sum()
            .reset_index()
            .rename(columns={"amount": "Total"})
        )
        cat_totals["color"] = cat_totals["category"].map(CATEGORY_COLORS)

        fig_pie = px.pie(
            cat_totals,
            values="Total",
            names="category",
            hole=0.38,
            color="category",
            color_discrete_map=CATEGORY_COLORS,
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Rs %{value:,.2f}<extra></extra>",
        )
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            margin=dict(t=10, b=10, l=10, r=10),
            height=380,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Bar chart: daily spending ─────────────────────────────────────────────
    with chart_right:
        st.markdown("#### 📅 Daily Spending This Month")

        daily = (
            monthly_df.groupby("date")["amount"]
            .sum()
            .reset_index()
            .rename(columns={"amount": "Total"})
        )
        daily["date"] = pd.to_datetime(daily["date"])
        daily = daily.sort_values("date")

        fig_bar = px.bar(
            daily,
            x="date",
            y="Total",
            labels={"date": "", "Total": "Amount (Rs)"},
            color_discrete_sequence=["#60A5FA"],
        )
        fig_bar.update_traces(
            hovertemplate="<b>%{x|%b %d}</b><br>Rs %{y:,.2f}<extra></extra>",
        )
        fig_bar.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=380,
            xaxis=dict(tickformat="%b %d", tickangle=-45),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ░░  EXPENSE TABLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## 📋 Expense History")

filter_cat = selected_category if selected_category != "All" else None
filtered_rows = db.get_expenses_filtered(
    category=filter_cat,
    start_date=start_date.isoformat(),
    end_date=end_date.isoformat(),
)

if not filtered_rows:
    st.info("No expenses match your current filters. Try adjusting the sidebar. 🔍")
else:
    df_show = pd.DataFrame(filtered_rows)

    # Friendly column names + formatted amount
    df_show = df_show.rename(
        columns={"name": "Name", "category": "Category", "amount": "Amount", "date": "Date"}
    )
    df_show["Amount"] = df_show["Amount"].apply(lambda x: f"Rs {x:,.2f}")
    df_show = df_show[["Date", "Name", "Category", "Amount"]].reset_index(drop=True)

    st.dataframe(
        df_show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date":     st.column_config.TextColumn("📅 Date",     width="small"),
            "Name":     st.column_config.TextColumn("🏷️ Name",     width="medium"),
            "Category": st.column_config.TextColumn("📂 Category", width="small"),
            "Amount":   st.column_config.TextColumn("💲 Amount",   width="small"),
        },
    )
    st.caption(f"Showing **{len(df_show)}** expense(s)  ·  Total: **Rs {sum(r['amount'] for r in filtered_rows):,.2f}**")

    # ── Download CSV button ───────────────────────────────────────────────────
    csv_data = df_show.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Report (CSV)",
        data=csv_data,
        file_name=f"expense_report_{start_date}_{end_date}.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# ░░  CLEAR ALL RECORDS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("## 🗑️ Manage Records")

with st.expander("⚠️ Clear All Expense Records", expanded=False):
    st.warning(
        "This will **permanently delete all expense records** from the database. "
        "This action cannot be undone."
    )
    confirm_clear = st.checkbox("Yes, I want to delete all records")
    if st.button("🗑️ Clear All Records", disabled=not confirm_clear, type="primary"):
        db.clear_all_expenses()
        st.success("✅ All records have been cleared! You can now add fresh expenses.")
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ░░  FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("💰 Personal Budget Tracker  ·  Data stored locally in budget.db")
