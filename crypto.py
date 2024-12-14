import json
from web3 import Web3

# Membaca konfigurasi dari file config.json
def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)

# Inisialisasi koneksi ke Ethereum menggunakan Infura dari config.json
config = load_config()
infura_url = f"https://mainnet.infura.io/v3/{config['infura_project_id']}"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Memeriksa apakah alamat kontrak valid
def is_valid_contract(address):
    return web3.isAddress(address)

# Memeriksa pemilik kontrak
def check_token_owner(contract_address):
    # ABI minimal untuk memeriksa pemilik kontrak
    abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "owner",
            "outputs": [{"name": "", "type": "address"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]

    # Cek apakah alamat kontrak valid
    if not is_valid_contract(contract_address):
        return "Alamat kontrak tidak valid."

    # Membuat objek kontrak
    contract = web3.eth.contract(address=contract_address, abi=abi)
    
    try:
        # Memanggil fungsi owner untuk mendapatkan alamat pemilik kontrak
        owner_address = contract.functions.owner().call()
        print(f"Pemilik kontrak: {owner_address}")

        # Cek apakah pemilik dapat melakukan rugpull (misalnya, jika owner adalah alamat kontrak kosong)
        if owner_address == "0x0000000000000000000000000000000000000000":
            return "Token aman dari rugpull: Pemilik kontrak adalah alamat nol."
        else:
            return "Peringatan: Token ini memiliki pemilik yang bisa mengubah kontrak atau likuiditas."
    
    except Exception as e:
        return f"Error memeriksa kontrak: {e}"

# Meminta input alamat kontrak token dari pengguna
def get_contract_address():
    contract_address = input("Masukkan alamat kontrak token: ")
    return contract_address

# Program utama
contract_address = get_contract_address()
result = check_token_owner(contract_address)
print(result)
