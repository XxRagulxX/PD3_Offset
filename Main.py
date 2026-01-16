import requests
import json
import secrets

# Step 1: Get the OAuth Token
string_length = 32
random_string = ''.join(secrets.choice(secrets.token_hex(16)) for _ in range(string_length))

def get_token():
    token_header = {
        "Host": "nebula.starbreeze.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic MGIzYmZkZjVhMjVmNDUyZmJkMzNhMzYxMzNhMmRlYWI6",  # Update this if needed
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Electron/25.8.3 Safari/537.36",
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US"
    }

    # Replace with actual credentials
    username = ""
    password = ""
    client_id = random_string  # Replace with your client ID

    data_token = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_id": client_id,
        "extend_exp": "true"
    }

    url_token = "https://nebula.starbreeze.com/iam/v3/oauth/token"

    response = requests.post(url_token, headers=token_header, data=data_token)

    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"Failed to get token. Status code: {response.status_code}")
        return None

# Step 2: Fetch the new data
def fetch_and_save_data(token):
    url = "https://nebula.starbreeze.com/platform/public/namespaces/pd3/items/byCriteria"
    headers = {
        "Connection": "Keep-Alive",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": f"Bearer {token}",
        "User-Agent": "PAYDAY3/++UE4+Release-4.27-CL-0 WinGDK/6.2.9200.1.256.64bit",
        "x-flight-id": "D95ABC824983E0DD92F8B7AE9D547206",
        "Namespace": "pd3",
        "Game-Client-Version": "1.0.0.0",
        "AccelByte-SDK-Version": "24.7.2",
        "AccelByte-OSS-Version": "0.12.1-2",
        "Host": "nebula.starbreeze.com",
        "Cookie": "access_token="
    }

    params = {
        "limit": 2147483647,
        "includeSubCategoryItem": "false"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return

    new_data = response.json()

    # Save the new data to a file
    output_filename = 'Payday3_Items.json'
    with open(output_filename, 'w') as json_file:
        json.dump(new_data, json_file, indent=4)

    print(f"Fetched data saved to {output_filename}")
    return new_data

# Step 3: Compare and categorize the data
def compare_and_categorize_data(new_data):
    old_filename = 'Shopping_Spree_Heist.json'  # Old data file
    new_filename = 'Payday3_Items.json'  # New data file

    with open(old_filename, 'r') as old_file:
        old_data = json.load(old_file)

    # Extract existing titles from old_data
    existing_titles = {item['title'] for item in old_data['data']}

    # Define categories in a specific-to-broad hierarchy
    categories_hierarchy = {
        "Attachments For Guns": ["MOD"],
        "Inventory Slots": ["Inventory Slot"],
        "Weapon Charms": ["Weapon Charm", "Charm"],
        "Preplanning Assets": ["Preplanning", "asset", "Ammo Bag", "Armor Bag", "Medic Bag"],
        "Mask Mould": ["Mask Mould", "mask mould"],
        "Tailor Packs": ["Tailor Pack", "Tailor", "Trifecta Lootbag"],
        "Masks": ["Mask"],
        "Suit": ["Suit"],
        "Heist Pack": ["Heist", "Data Center Steam"],
        "Weapon Patterns": ["Weapon Pattern"],
        "Weapon Stickers": ["Weapon Sticker"],
        "Weapon Packs": ["Weapon Pack", "Weapon", "Pack"],
        "Mask Patterns": ["Mask Pattern"],
        "Spray Paints": ["Paint", "SprayCan"],
        "Compensation Bundle": ["Compensation Bundle"],
        "Base Preset": ["Base Preset", "Preset"],
        "Gloves Items": ["Gloves"],
        "Characters": ["Character"],
        "Twitch Items": ["Twitch"],
        "Gadgets": ["Tool", "tool", "Sentry Gun", "Shock Grenade", "Smoke Grenade", "ThrowingKnife", "Vest"],
        "Gold Purchase": ["Gold"],
        "Other": []
    }

    platforms = ["PlayStation", "Epic", "Xbox", "Steam"]
    guns = ["Pistol", "Marksman", "LMG", "SMG", "Shotgun", "Rifle", "Revolver", "AssaultRifle", "Overkill"]

    def find_platform(title):
        for platform in platforms:
            if platform.lower() in title.lower():
                return platform
        return None

    def find_gun(title):
        for gun in guns:
            if gun.lower() in title.lower():
                return gun
        return None

    def is_vendor_item(title):
        return "Vendor Item" in title

    def categorize_item(title):
        title_lower = title.lower()

        if "twitch drops" in title_lower:
            return "Twitch Items"

        platform = find_platform(title)
        gun = find_gun(title)

        if gun:
            if platform:
                return f"{platform} Guns"
            return "Guns"

        for category, keywords in categories_hierarchy.items():
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    if platform:
                        return f"{platform} {category}"
                    return category
        return "Other"

    final_data = {}

    for item in new_data['data']:
        title = item['title']

        if title not in existing_titles:
            title = f"{title} *new*"

        category = categorize_item(title)

        new_item = {
            title: {
                "itemId": item['itemId'],
                "price": item['regionData'][0]['price'],
                "discountedPrice": item['regionData'][0]['discountedPrice'],
                "currency": item['regionData'][0]['currencyCode']
            }
        }

        if category not in final_data:
            final_data[category] = []

        final_data[category].append((new_item, is_vendor_item(item['title'])))

    # Sort each category so that vendor items appear last
    for category, items in final_data.items():
        final_data[category] = [item for item, is_vendor in sorted(items, key=lambda x: x[1])]

    # Save the modified data to a new JSON file
    output_filename = 'categorized_new_data.json'
    with open(output_filename, 'w') as json_file:
        json.dump(final_data, json_file, indent=4)

    print(f"Data has been categorized and saved to {output_filename}")

# Main Execution Flow
if __name__ == "__main__":
    token = get_token()
    if token:
        new_data = fetch_and_save_data(token)
        if new_data:
            compare_and_categorize_data(new_data)
    else:
        print("Token generation failed. Exiting.")
