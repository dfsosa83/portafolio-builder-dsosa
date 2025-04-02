import yfinance as yf

def fetch_stock_data(symbol, period="1y"):
    """
    Fetches historical stock data for a given symbol.
    Args:
        symbol (str): Stock symbol (e.g., "AAPL").
        period (str): Time period (e.g., "1y", "5y").
    Returns:
        pandas.DataFrame: Historical data.
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data
    except Exception as e:
        raise ValueError(f"Failed to fetch data for {symbol}: {str(e)}")

def fetch_current_price(symbol):
    """
    Fetches the current price of a stock.
    """
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info.get("currentPrice", "N/A")
    except Exception as e:
        raise ValueError(f"Failed to fetch price for {symbol}: {str(e)}")
