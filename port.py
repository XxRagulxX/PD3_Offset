import json
import re

def load_json(filename):
    with open(filename, encoding="utf-8") as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_item_name(item):
    # Each item is a dict with a single key
    return next(iter(item.keys()))

def should_skip(name):
    return re.search(r"xbox|playstation", name, re.IGNORECASE)

def update_paste(paste, paste2):
    for category, items2 in paste2.items():
        if category not in paste:
            paste[category] = []
        # Build a set of existing item names for this category
        existing_names = set(get_item_name(item) for item in paste[category])
        for item2 in items2:
            name2 = get_item_name(item2)
            if should_skip(name2):
                continue
            if name2 not in existing_names:
                paste[category].append(item2)
                existing_names.add(name2)
    return paste

if __name__ == "__main__":
    # Load the files
    with open("offsets.json", encoding="utf-8") as f:
        paste = json.load(f)
    with open("categorized_new_data.json", encoding="utf-8") as f:
        paste2 = json.load(f)

    # Update
    updated = update_paste(paste, paste2)

    # Save back to paste.txt
    with open("updatedfile.json", "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=4, ensure_ascii=False)

    print("paste.txt updated successfully!")
