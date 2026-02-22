import streamlit as st
import json
import os
import plotly.express as px
import pandas as pd
from modules.storage import save_transaction, load_transactions, clear_all
from modules.categorizer import categorize
from modules.analyzer import total_by_category, check_budget, detect_unusual, predict_month_end

st.set_page_config(page_title="Finance Tracker", page_icon="💰", layout="wide")

st.sidebar.title("💰 Finance Tracker")
page = st.sidebar.radio("Navigate", ["Add Transaction", "Dashboard", "Insights", "Set Budget"])

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
            save_transaction({
                "date": str(date),
                "description": description,
                "amount": final_amount,
                "category": category
            })
            st.success(f"✅ Saved! Categorized as: {category}")

elif page == "Dashboard":
    st.title("Dashboard")
    transactions = load_transactions()
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

        BUDGET_FILE = "data/budget.json"
        if os.path.exists(BUDGET_FILE):
            with open(BUDGET_FILE, "r") as f:
                budget = json.load(f)
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

elif page == "Insights":
    st.title("Insights")
    transactions = load_transactions()
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

elif page == "Set Budget":
    st.title("Set Your Budget")
    BUDGET_FILE = "data/budget.json"
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            current_budget = json.load(f)
    else:
        current_budget = {}
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
        with open(BUDGET_FILE, "w") as f:
            json.dump(new_budget, f, indent=4)
        st.success("✅ Budget saved!")
    if current_budget:
        st.subheader("Current Budget Limits")
        for cat, limit in current_budget.items():
            st.write(f"**{cat}:** ${limit:.2f}")