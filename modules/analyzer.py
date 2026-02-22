import statistics
from datetime import datetime
def total_by_category(transactions):
    totals = {}
    for t in transactions:
        category = t["category"]
        amount = abs(t["amount"])
        if t["amount"] < 0:
            if category not in totals:
                totals[category] = 0
            totals[category] += amount
    return totals
def check_budget(totals, budget):
    warnings = []
    for category, limit in budget.items():
        spent = totals.get(category, 0)
        if spent > limit:
            warnings.append(f"OVER BUDGET- {category}: spent \${spent:.2f} but budget is \${limit:.2f}")
    return warnings
def detect_unusual(transactions):
    flagged = []
    by_category = {}
    for t in transactions:
        if t["amount"] < 0 and t["category"] != "":
            cat = t["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(abs(t["amount"]))
    for t in transactions:
        if t["amount"] < 0 and t["category"] != "":
            cat = t["category"]
            amounts = by_category[cat]
            if len(amounts) >= 2:
                avg = statistics.mean(amounts)
                if abs(t["amount"]) > avg * 2:
                    flagged.append(f"🚨 Unusual: {t['description']} (${abs(t['amount']):.2f}) is way above your average for {cat}")
    return flagged
def predict_month_end(transactions):
    today = datetime.today()
    days_so_far = today.day
    total_spent = sum(abs(t["amount"]) for t in transactions if t["amount"] < 0)
    if days_so_far == 0:
        return 0
    daily_average = total_spent / days_so_far
    predicted = daily_average * 30
    return round(predicted, 2)
