import json         #a way of saving python data as a readable text in a file.
import os           #this lets python

FILEPATH ="data/transactions.json"

def save_transaction(transaction):
    transactions = load_transactions()
    transactions.append(transaction)
    with open(FILEPATH, "w") as f:
        json.dump(transactions, f, indent=4)

def load_transactions():
    if not os.path.exists(FILEPATH):
        return []
    with open(FILEPATH, "r") as f:
        return json.load(f)

def clear_all():
    with open(FILEPATH,"w") as f:
        json.dump([], f)
        