import json
import urllib.request
import urllib.error

# Fungsi untuk memuat pengaturan dari file config.json
def load_config():
    with open('config.json') as config_file:
        config = json.load(config_file)
    return config

# Memuat pengaturan
config = load_config()

# Mengakses API Key dari config.json
API_KEY = config['bscscan_api_key']
min_holders = config['check_criteria']['min_holders']
min_holder_ratio = config['check_criteria']['min_holder_ratio']
max_supply_percentage = config['check_criteria']['max_supply_percentage']

# Fungsi untuk mendapatkan data dari BscScan API
def check_token(address):
    url = f"https://api.bscscan.com/api?module=token&action=getTokenInfo&contractaddress={address}&apikey={API_KEY}"
    
    try:
        # Mengirim permintaan HTTP GET menggunakan urllib
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
        
        if data["status"] == "1":
            return data["result"]
        else:
            return None
    except urllib.error.URLError as e:
        print(f"Error fetching data: {e}")
        return None

# Fungsi untuk memeriksa potensi rugpull
def analyze_rugpull(token_data):
    if token_data:
        holders = int(token_data["holdersCount"])
        total_supply = int(token_data["totalSupply"])
        circulating_supply = int(token_data["circulatingSupply"])
        
        if holders < min_holders or holders / total_supply < min_holder_ratio:
            return "Token berisiko rugpull: jumlah holder terlalu sedikit"
        if circulating_supply > total_supply * max_supply_percentage:
            return "Token berisiko rugpull: persentase sirkulasi supply terlalu tinggi"
        
        return "Token aman, tetapi tetap waspada"
    else:
        return "Data token tidak ditemukan."

# Input contract address
address = input("Masukkan contract address token: ")

# Mengecek dan menganalisis token
token_data = check_token(address)
result = analyze_rugpull(token_data)
print(result)
