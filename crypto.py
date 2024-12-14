import requests
import json

def get_token_data(contract_address):
    url = f'https://api.dexscreener.com/latest/dex/tokens/{contract_address}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        # Simpan data JSON ke file
        with open("token_data.json", "w") as json_file:
            json.dump(data, json_file, indent=4)
        
        if 'pair' in data:
            token_data = data['pair']
            token_name = token_data['baseToken']['symbol']
            price = token_data['priceUsd']
            volume = token_data['volumeUsd24h']
            change_24h = token_data['priceChange24h']

            print(f"Token: {token_name}")
            print(f"Price (USD): ${price}")
            print(f"24h Volume (USD): ${volume}")
            print(f"24h Change: {change_24h}%")

            # Simple analysis: If price change is positive, it's a good sign
            if change_24h > 0:
                print("The token is showing positive momentum!")
            else:
                print("The token is showing negative momentum.")
        else:
            print("Data not found for the given contract address.")
    else:
        print(f"Error fetching data: {response.status_code}")

# Example usage
contract_address = input("Enter the token contract address: ")
get_token_data(contract_address)
