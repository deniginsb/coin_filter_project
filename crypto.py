import subprocess
import json

# Membaca konfigurasi dari file config.json
def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

# Fungsi untuk mengirim permintaan API menggunakan curl
def send_api_request(url):
    command = ["curl", "-X", "GET", url]
    result = subprocess.run(command, capture_output=True, text=True)
    return json.loads(result.stdout)

# Fungsi untuk mendapatkan informasi kontrak token dari Etherscan
def get_contract_info(address, api_key):
    url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={api_key}"
    
    response = send_api_request(url)
    
    if response['status'] == '1':  # Status '1' berarti request berhasil
        return response['result']
    else:
        return f"Error: {response['message']}"

# Fungsi untuk memeriksa jika kontrak dapat berpotensi rugpull
def check_risk_of_rugpull(address, api_key):
    abi = get_contract_info(address, api_key)
    
    if "burn" in abi or "transfer" in abi:
        return "Kontrak berpotensi rugpull jika ada fungsi yang memungkinkan pengembang menarik likuiditas atau mengendalikan token."
    else:
        return "Kontrak tidak ditemukan indikasi risiko rugpull."

# Mengambil data dari config.json
config = load_config()

# Meminta input alamat kontrak dari pengguna
contract_address = input("Masukkan alamat kontrak token: ")
etherscan_api_key = config["etherscan_api_key"]

# Memeriksa risiko rugpull
risk_info = check_risk_of_rugpull(contract_address, etherscan_api_key)
print(risk_info)
