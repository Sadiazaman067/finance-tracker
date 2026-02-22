CATEGORIES = {
    "Food & Dining":  ["starbucks", "chick-fil-a", "chick fil a", "doordash", "uber eats", "restaurant", "pizza", "kfc", "subway", "panda express", "in & out"],
    "Transport":      ["uber", "lyft", "gas", "parking", "bus", "train", "bolt", "plane", "flight"],
    "Shopping":       ["amazon", "walmart", "target", "fashion nova", "shein", "temu", "online order", "online"],
    "Bills":          ["electricity", "water", "internet", "phone", "rent", "netflix", "spotify", "disney+", "mortgage"],
    "Entertainment":  ["cinema", "movies", "games", "steam", "youtube", "game night"],
    "Income":         ["salary", "paycheck", "freelance", "transfer in", "deposit"],
}

def categorize(description):
    description_lower = description.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    return "Other"