from fpdf import FPDF
from datetime import datetime
def generate_monthly_report(transactions, budget):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    
    # Title
    pdf.cell(0, 10, "Monthly Finance Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Generated: {datetime.today().strftime('%B %d, %Y')}", ln=True, align="C")
    pdf.ln(10)
    # Income vs Expenses
    total_income = sum(t["amount"] for t in transactions if t["amount"] > 0)
    total_expenses = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
    balance = total_income - total_expenses
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Summary", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Total Income:   ${total_income:.2f}", ln=True)
    pdf.cell(0, 8, f"Total Expenses: ${total_expenses:.2f}", ln=True)
    pdf.cell(0, 8, f"Balance:        ${balance:.2f}", ln=True)
    pdf.ln(8)
    # Spending by category
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Spending by Category", ln=True)
    pdf.set_font("Helvetica", "", 12)
    totals = {}
    for t in transactions:
        if t["amount"] < 0:
            cat = t["category"] or "Other"
            totals[cat] = totals.get(cat, 0) + abs(t["amount"])
    for cat, amount in totals.items():
        limit = budget.get(cat, 0)
        status = "OVER BUDGET" if amount > limit and limit > 0 else "OK"
        pdf.cell(0, 8, f"{cat}: ${amount:.2f} / budget ${limit:.2f} - {status}", ln=True)
    pdf.ln(8)
    # All transactions
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "All Transactions", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for t in transactions:
        line = f"{t['date']}  |  {t['description']}  |  ${abs(t['amount']):.2f}  |  {t['category']}"
        pdf.cell(0, 7, line, ln=True)
    return pdf.output()