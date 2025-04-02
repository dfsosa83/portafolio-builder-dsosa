from data_fetcher import fetch_stock_data, fetch_current_price

# Test fetching historical stock data
symbol = "AAPL"  # Apple Inc.
print(f"Fetching historical data for {symbol}...")
stock_data = fetch_stock_data(symbol)
print(stock_data.head())  # Display the first few rows of data

# Test fetching the current price
print(f"Fetching current price for {symbol}...")
current_price = fetch_current_price(symbol)
print(f"Current price of {symbol}: ${current_price}")
