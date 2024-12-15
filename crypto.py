import requests
import json

# Fungsi untuk mengambil data dari Dexscreener
def get_dexscreener_data():
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data from Dexscreener, Status Code: {response.status_code}")
        return None

# Fungsi untuk mengambil data dari API de.fi dengan tokenAddress
def get_defi_data(token_address, api_key):
    url = f"https://de.fi/api/{token_address}"  # Sesuaikan URL dengan API de.fi
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    
    # Cek status code
    if response.status_code == 200:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print("Error: Response from de.fi is not in valid JSON format.")
            return None
    else:
        print(f"Error fetching data from de.fi, Status Code: {response.status_code}")
        return None

# Fungsi utama untuk menjalankan alur
def process_data():
    # Langkah 1: Ambil data dari Dexscreener
    dexscreener_data = get_dexscreener_data()
    if not dexscreener_data:
        print("Error fetching data from Dexscreener.")
        return

    # Langkah 2: Ekstrak tokenAddress dari Dexscreener
    token_address = dexscreener_data.get("tokenAddress")
    if not token_address:
        print("Token address not found in Dexscreener data.")
        return
    
    # Langkah 3: Ambil API key dari file konfigurasi
    with open("config.json", "r") as f:
        config = json.load(f)
    api_key = config["defi_api_key"]

    # Langkah 4: Ambil data dari de.fi menggunakan tokenAddress
    defi_data = get_defi_data(token_address, api_key)
    if not defi_data:
        print("Error fetching data from de.fi.")
        return

    # Langkah 5: Tampilkan data dari de.fi (atau proses sesuai kebutuhan)
    print(f"Data from de.fi for token {token_address}:")
    print(defi_data)

# Jalankan proses
process_data()
