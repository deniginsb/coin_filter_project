import requests
import pandas as pd
import json

class CoinFilter:
    def __init__(self, config_file="config.json"):
        self.pumpfun_url = "https://pump.fun/advanced"
        self.dexscreener_url = "https://api.dexscreener.com/latest/dex/tokens"
        self.rugcheck_url = ""
        self.tweetscout_url = ""
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Memuat konfigurasi dari file."""
        try:
            with open(self.config_file, "r") as file:
                config = json.load(file)
                self.rugcheck_url = config.get("rugcheck_url", "")
                self.tweetscout_url = config.get("tweetscout_url", "")
                print("Konfigurasi berhasil dimuat.")
                return config
        except FileNotFoundError:
            print("File konfigurasi tidak ditemukan.")
            return {"blacklisted_tokens": [], "blacklisted_developers": []}

    def save_config(self):
        """Menyimpan konfigurasi ke file."""
        with open(self.config_file, "w") as file:
            json.dump(self.config, file, indent=4)
            print("Konfigurasi berhasil disimpan.")

    def fetch_pumpfun_data(self):
        """Mengambil data dari PumpFun."""
        response = requests.get(self.pumpfun_url)
        if response.status_code == 200:
            print("Data PumpFun berhasil diambil.")
            return response.json()
        else:
            print("Gagal mengambil data PumpFun.")
            return None

    def fetch_dexscreener_data(self):
        """Mengambil data dari DexScreener."""
        response = requests.get(self.dexscreener_url)
        if response.status_code == 200:
            print("Data DexScreener berhasil diambil.")
            return response.json()
        else:
            print("Gagal mengambil data DexScreener.")
            return None

    def validate_with_rugcheck(self, token_address):
        """Validasi token menggunakan API RugCheck."""
        if not self.rugcheck_url:
            print("RugCheck URL tidak ditemukan dalam konfigurasi.")
            return False

        params = {"token_address": token_address}
        response = requests.get(self.rugcheck_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "Baik" and not data.get("is_bundled", True):
                return True  # Token valid jika status "Baik" dan tidak dibundel
            else:
                print(f"Token {token_address} tidak valid: {data}")
                return False
        else:
            print(f"Gagal memvalidasi token {token_address} dengan RugCheck.")
            return False

    def fetch_twitter_score(self, token_symbol):
        """Mengecek skor Twitter token menggunakan API TweetScout."""
        if not self.tweetscout_url:
            print("TweetScout URL tidak ditemukan dalam konfigurasi.")
            return "Tidak Valid"

        params = {"token_symbol": token_symbol}
        response = requests.get(self.tweetscout_url, params=params)
        if response.status_code == 200:
            data = response.json()
            score = data.get("score", 0)
            if score >= 450:
                return "Baik"
            else:
                return "Sedang"
        else:
            print(f"Gagal memvalidasi skor Twitter untuk {token_symbol}.")
            return "Tidak Valid"

    def blacklist_token_and_developer(self, token_name, developer):
        """Tambahkan token dan developer ke daftar hitam."""
        if token_name not in self.config["blacklisted_tokens"]:
            self.config["blacklisted_tokens"].append(token_name)
            print(f"Token {token_name} ditambahkan ke daftar hitam.")
        
        if developer and developer not in self.config["blacklisted_developers"]:
            self.config["blacklisted_developers"].append(developer)
            print(f"Pengembang {developer} ditambahkan ke daftar hitam.")
        
        self.save_config()

    def filter_tokens(self, tokens):
        """Memfilter token berdasarkan kriteria, validasi RugCheck, dan skor Twitter."""
        filtered_tokens = []
        blacklisted_tokens = self.config.get("blacklisted_tokens", [])
        blacklisted_developers = self.config.get("blacklisted_developers", [])

        for token in tokens:
            token_name = token.get("symbol", "")
            developer = token.get("developer", "")  # Asumsikan ada data developer di API
            age = token.get("pairAge", 0)  # Usia pasangan dalam jam
            transactions_1h = token.get("transactions", {}).get("1h", 0)
            transactions_5m = token.get("transactions", {}).get("5m", 0)
            token_address = token.get("address", "")

            if (token_name in blacklisted_tokens or 
                developer in blacklisted_developers or 
                age > 24 or 
                transactions_1h < 150 or 
                transactions_5m < 25):
                continue

            # Validasi dengan RugCheck
            if not self.validate_with_rugcheck(token_address):
                self.blacklist_token_and_developer(token_name, developer)
                continue

            # Validasi skor Twitter
            twitter_score = self.fetch_twitter_score(token_name)
            if twitter_score != "Baik":
                print(f"Token {token_name} gagal validasi Twitter dengan skor: {twitter_score}")
                continue

            filtered_tokens.append(token)
        return filtered_tokens

    def process(self):
        """Proses utama untuk mengambil, memfilter, dan menganalisis data."""
        pumpfun_data = self.fetch_pumpfun_data()
        if pumpfun_data is None:
            return

        dexscreener_data = self.fetch_dexscreener_data()
        if dexscreener_data is None:
            return

        tokens = dexscreener_data.get("pairs", [])
        filtered_tokens = self.filter_tokens(tokens)

        results = []
        for token in filtered_tokens:
            token_address = token.get("address", "")
            results.append({"token": token})

        # Simpan hasil ke file CSV
        df = pd.DataFrame(results)
        df.to_csv("filtered_tokens.csv", index=False)
        print("Hasil berhasil disimpan di 'filtered_tokens.csv'.")

if __name__ == "__main__":
    coin_filter = CoinFilter()
    coin_filter.process()
