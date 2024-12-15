import requests
import json

# Fungsi untuk membaca konfigurasi dari file config.json
def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config

# Fungsi untuk mengambil data dari Dexscreener
def get_dexscreener_data(config):
    url = config["dexscreener_url"]
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# Fungsi untuk mengambil data dari API de.fi
def get_defi_data(config):
    api_key = config["defi_api_key"]
    url = config["defi_url"]
    headers = {
        "Authorization": f"Bearer {api_key}"  # Menambahkan API key dalam header otentikasi
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

# Fungsi utama untuk menjalankan alur
def process_data():
    # Membaca konfigurasi dari file config.json
    config = load_config()

    # Langkah 1: Ambil data dari Dexscreener
    dexscreener_data = get_dexscreener_data(config)
    if not dexscreener_data:
        print("Error fetching data from Dexscreener.")
        return

    # Langkah 2: Setelah Dexscreener data diterima, ambil data dari de.fi
    defi_data = get_defi_data(config)
    if not defi_data:
        print("Error fetching data from de.fi.")
        return

    # Langkah 3: Gabungkan data dari Dexscreener dan de.fi
    combined_data = dexscreener_data["data"] + defi_data["tokens"]

    # Langkah 4: Filter dan analisis data untuk menemukan koin micin
    micin_coins = []
    for coin in combined_data:
        if coin.get("price_usd", 0) < 1:  # Misalnya filter berdasarkan harga koin < 1 USD
            micin_coins.append(coin)

    # Tampilkan hasilnya
    if micin_coins:
        print("Koin Micin Ditemukan:")
        for coin in micin_coins:
            print(f"Name: {coin.get('name')}, Price: {coin.get('price_usd')}")
    else:
        print("Tidak ada koin micin ditemukan.")

# Jalankan proses
process_data()
