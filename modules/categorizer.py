CATEGORIES = {
    "Food & Dining": ["starbucks", "in & out", "uber eats", "restaurant", "pizza", "chick fil a", "subway", "Panda Express"],
    "Transport":      ["uber", "lyft", "gas", "parking", "bus", "train", "bolt", "flight"],
    "Shopping":       ["amazon", "walmart", "target", "shein", "Temu", "online order"],
    "Bills":          ["electricity", "water", "internet", "phone", "rent", "netflix", "spotify", "mortgage"],
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
