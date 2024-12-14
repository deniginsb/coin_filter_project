import requests
import json
import os

# === Konfigurasi ===
CONFIG_FILE = "settings.json"

# Memuat atau membuat file konfigurasi default
def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "developer_blacklist": [],
            "memecoin_blacklist": [],
            "pumpfun_url": "https://pump.fun/advanced",
            "dexscreener_url": "https://api.dexscreener.com/latest/dex/tokens",
            "gmgn_url": "https://gmgn.ai",
            "rocker_universe_url": "https://api.rockeruniverse.com/check",
            "rugcheck_url": "http://rugcheck.xyz",
            "tweetscout_url": "http://app.tweetscout.io/api/twitter_score",
            "filters": {
                "max_pair_age_hours": 24,
                "min_1h_transactions": 150,
                "min_5m_transactions": 25
            }
        }
        with open(CONFIG_FILE, "w") as file:
            json.dump(default_config, file, indent=4)
        return default_config
    else:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)

# Simpan perubahan ke file konfigurasi
def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

# Memuat konfigurasi
config = load_config()

# === Tweetscout: Pemeriksaan Skor Twitter ===
def get_twitter_score(token_name):
    """Periksa skor Twitter token melalui Tweetscout API."""
    url = config["tweetscout_url"]
    try:
        # Misalnya, token_name digunakan untuk mencari tweet terkait token di Twitter
        response = requests.get(f"{url}?token={token_name}")
        response.raise_for_status()
        result = response.json()
        score = result.get("score", 0)
        if score > 450:
            print(f"Token {token_name} has a good Twitter score: {score}. Marked as 'Good'.")
            return "Good"
        else:
            print(f"Token {token_name} has a moderate Twitter score: {score}. Marked as 'Moderate'.")
            return "Moderate"
    except Exception as e:
        print(f"Error fetching Twitter score for {token_name}: {e}")
        return "Unknown"

# === RugCheck: Verifikasi Token ===
def is_token_safe(token_address):
    """Periksa status token di RugCheck."""
    url = config["rugcheck_url"]
    try:
        response = requests.get(f"{url}/api/check/{token_address}")
        response.raise_for_status()
        result = response.json()
        return result.get("status") == "Good"  # Pastikan token memiliki status "Good"
    except Exception as e:
        print(f"Error checking RugCheck for token {token_address}: {e}")
        return False

# === Verifikasi Pasokan Tidak Dibundel ===
def is_supply_bundled(token):
    """
    Verifikasi apakah pasokan koin dibundel berdasarkan pola distribusi
    (contoh sederhana: periksa jika pemegang utama terlalu besar).
    """
    total_supply = token.get("total_supply", 0)
    holders = token.get("holders", [])
    if not total_supply or not holders:
        return False

    # Ambil pemegang dengan alokasi terbesar
    largest_holder = max(holders, key=lambda h: h["amount"], default={"amount": 0})
    if largest_holder["amount"] / total_supply > 0.5:  # >50% dari total pasokan
        print(f"Token {token['name']} is bundled: largest holder owns more than 50%.")
        return True
    return False

# Tambahkan token dan pengembang ke daftar hitam
def blacklist_token_and_developer(token):
    if token["name"] not in config["memecoin_blacklist"]:
        config["memecoin_blacklist"].append(token["name"])
    if token["developer"] not in config["developer_blacklist"]:
        config["developer_blacklist"].append(token["developer"])
    save_config(config)
    print(f"Token {token['name']} and developer {token['developer']} blacklisted.")

# === DexScreener: Filter token baru ===
def fetch_dexscreener_data():
    url = config["dexscreener_url"]
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"DexScreener: Fetched {len(data['tokens'])} tokens.")
        return data['tokens']
    except Exception as e:
        print(f"Error fetching DexScreener data: {e}")
        return []

def filter_dexscreener_data(tokens):
    filters = config["filters"]
    filtered_tokens = []
    for token in tokens:
        if token.get("developer") in config["developer_blacklist"]:
            print(f"Skipping token {token['name']} by blacklisted developer {token['developer']}.")
            continue
        if token.get("name") in config["memecoin_blacklist"]:
            print(f"Skipping blacklisted memecoin {token['name']}.")
            continue
        if token.get("pair_age_hours", 0) > filters["max_pair_age_hours"] or \
           token.get("transactions_1h", 0) < filters["min_1h_transactions"] or \
           token.get("transactions_5m", 0) < filters["min_5m_transactions"]:
            continue
        if not is_token_safe(token["address"]):
            print(f"Skipping token {token['name']} as it is marked unsafe by RugCheck.")
            continue
        if is_supply_bundled(token):
            blacklist_token_and_developer(token)
            continue
        # Periksa skor Twitter untuk setiap token
        twitter_score = get_twitter_score(token["name"])
        token["twitter_score"] = twitter_score  # Menyimpan hasil skor Twitter
        filtered_tokens.append(token)
    print(f"DexScreener: Filtered to {len(filtered_tokens)} tokens after blacklist, criteria, and safety checks.")
    return filtered_tokens

# === Main Program ===
def main():
    print("Fetching data from DexScreener...")
    dexscreener_data = fetch_dexscreener_data()
    filtered_dexscreener = filter_dexscreener_data(dexscreener_data)
    
    print("Final filtered tokens:")
    for token in filtered_dexscreener:
        print(f"- {token['name']} ({token['address']}) | Twitter Score: {token.get('twitter_score', 'N/A')}")

if __name__ == "__main__":
    main()
        
