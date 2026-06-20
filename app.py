import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from modules.database import (init_db, register_user, login_user,
                               save_transaction, load_transactions,
                               save_budget, load_budget)
from modules.categorizer import categorize
from modules.analyzer import total_by_category, check_budget, detect_unusual, predict_month_end

st.set_page_config(page_title="PennyBloom", page_icon="🌸", layout="wide")

# Initialize database
init_db()

# ── SESSION STATE SETUP ──────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "name" not in st.session_state:
    st.session_state.name = ""

# ── AUTH PAGES ───────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.title("🌸 PennyBloom")
    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        st.subheader("Welcome back!")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            name = login_user(login_username, login_password)
            if name:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.session_state.name = name
                st.rerun()
            else:
                st.error("Incorrect username or password!")

    with tab2:
        st.subheader("Join PennyBloom!")
        reg_name = st.text_input("Full Name", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_username = st.text_input("Choose a Username", key="reg_user")
        reg_password = st.text_input("Choose a Password", type="password", key="reg_pass")
        reg_password2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
        if st.button("Create Account"):
            if not reg_name or not reg_email or not reg_username or not reg_password:
                st.warning("Please fill in all fields!")
            elif reg_password != reg_password2:
                st.error("Passwords don't match!")
            elif len(reg_password) < 6:
                st.warning("Password must be at least 6 characters!")
            else:
                success = register_user(reg_username, reg_name, reg_email, reg_password)
                if success:
                    st.success("✅ Account created! You can now log in.")
                else:
                    st.error("Username or email already exists!")

else:
    username = st.session_state.username
    name = st.session_state.name

    # ── SIDEBAR ──────────────────────────────────────────────────────────
    st.sidebar.title(f"🌸 Welcome, {name}!")
    page = st.sidebar.radio("Navigate", ["Add Transaction", "Dashboard", "Insights", "Set Budget"])
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.name = ""
        st.rerun()

    # ── ADD TRANSACTION ──────────────────────────────────────────────────
    if page == "Add Transaction":
        st.title("Add a Transaction")
        description = st.text_input("Description (e.g. Starbucks, Uber ride)")
        amount = st.number_input("Amount", step=0.01)
        transaction_type = st.radio("Type", ["Expense", "Income"])
        date = st.date_input("Date")
        if st.button("Save Transaction"):
            if description == "":
                st.warning("Please enter a description!")
            else:
                category = categorize(description)
                final_amount = -abs(amount) if transaction_type == "Expense" else abs(amount)
                save_transaction(username, {
                    "date": str(date),
                    "description": description,
                    "amount": final_amount,
                    "category": category
                })
                st.success(f"✅ Saved! Categorized as: {category}")

    # ── DASHBOARD ────────────────────────────────────────────────────────
    elif page == "Dashboard":
        st.title("Dashboard")
        transactions = load_transactions(username)
        if len(transactions) == 0:
            st.info("No transactions yet! Add some first.")
        else:
            totals = total_by_category(transactions)
            total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
            total_expenses = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"${total_income:.2f}")
            col2.metric("Total Expenses", f"${total_expenses:.2f}")
            col3.metric("Balance", f"${total_income - total_expenses:.2f}")

            budget = load_budget(username)
            if budget:
                budget_warnings = check_budget(totals, budget)
                if budget_warnings:
                    st.subheader("⚠️ Budget Warnings")
                    for w in budget_warnings:
                        st.error(f"⚠️ {w}")
                else:
                    st.success("✅ You're within budget on everything!")

            st.subheader("Spending by Category")
            if totals:
                fig = px.bar(
                    x=list(totals.keys()),
                    y=list(totals.values()),
                    labels={"x": "Category", "y": "Amount ($)"},
                    color=list(totals.keys())
                )
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("All Transactions")
            df = pd.DataFrame(transactions)
            st.dataframe(df, use_container_width=True)

    # ── INSIGHTS ─────────────────────────────────────────────────────────
    elif page == "Insights":
        st.title("Insights")
        transactions = load_transactions(username)
        if len(transactions) == 0:
            st.info("No transactions yet! Add some first.")
        else:
            prediction = predict_month_end(transactions)
            unusual = detect_unusual(transactions)

            st.subheader("📅 Month End Prediction")
            st.metric("Predicted Monthly Spending", f"${prediction:.2f}")

            st.subheader("🚨 Unusual Transactions")
            if len(unusual) == 0:
                st.success("No unusual spending detected!")
            else:
                for flag in unusual:
                    st.warning(flag)

            st.subheader("🥧 Spending Breakdown")
            totals = total_by_category(transactions)
            if totals:
                fig = px.pie(
                    values=list(totals.values()),
                    names=list(totals.keys()),
                    title="Where your money is going"
                )
                st.plotly_chart(fig, use_container_width=True)

    # ── SET BUDGET ───────────────────────────────────────────────────────
    elif page == "Set Budget":
        st.title("Set Your Budget")
        current_budget = load_budget(username)

        st.subheader("Set monthly limits for each category")
        categories = ["Food & Dining", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
        new_budget = {}

        for category in categories:
            default = current_budget.get(category, 0.0)
            new_budget[category] = st.number_input(
                f"{category} ($)",
                value=float(default),
                step=10.0,
                min_value=0.0
            )

        if st.button("Save Budget"):
            save_budget(username, new_budget)
            st.success("✅ Budget saved!")

        if current_budget:
            st.subheader("Current Budget Limits")
            for cat, limit in current_budget.items():
                st.write(f"**{cat}:** ${limit:.2f}")

        st.divider()
        st.subheader("📄 Download Monthly Report")
        transactions = load_transactions(username)
        if len(transactions) == 0:
            st.info("No transactions yet to generate a report!")
        else:
            from modules.reports import generate_monthly_report
            pdf_bytes = generate_monthly_report(transactions, current_budget)
            st.download_button(
                label="📥 Download PDF Report",
                data=bytes(pdf_bytes),
                file_name=f"pennybloom_report_{datetime.today().strftime('%B_%Y')}.pdf",
                mime="application/pdf"
            )

