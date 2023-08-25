import requests

class Cryptocurrency:
    def __init__(self, name, symbol):
        """
        Initialize a Cryptocurrency instance.

        Args:
            name (str): The name of the cryptocurrency.
            symbol (str): The symbol or ticker of the cryptocurrency (e.g., BTC).
        """
        self.name = name
        self.symbol = symbol
        self.market_data = {}  # Dictionary to store real-time data

    def get_realtime_data(self):
        """
        Fetch real-time data for the cryptocurrency using the Binance API.

        Returns:
            dict: Real-time market data for the cryptocurrency (e.g., price, volume).
        """
        try:
            # Define the Binance API endpoint for the cryptocurrency's ticker symbol
            binance_api_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={self.symbol}USDT"

            # Make a GET request to fetch real-time data
            response = requests.get(binance_api_url)
            data = response.json()

            # Extract relevant data and store it in self.market_data
            self.market_data["symbol"] = data["symbol"]
            self.market_data["price"] = float(data["lastPrice"])
            self.market_data["volume"] = float(data["quoteVolume"])
            self.market_data["timestamp"] = data["closeTime"]

            return self.market_data

        except Exception as e:
            # Handle exceptions (e.g., network issues, API errors)
            print(f"Error fetching data for {self.symbol}: {e}")
            return None

# Example usage:
# btc = Cryptocurrency("Bitcoin", "BTC")
# btc_data = btc.get_realtime_data()
# print(btc_data)
