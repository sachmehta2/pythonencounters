from nsepy.history import get_price_list
from datetime import datetime
import pandas as pd

def is_market_open():
    """Check if the market is open today."""
    today = datetime.now().date()
    # Example: Check if today is a weekend (Saturday or Sunday)
    if today.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        return False
    # Add logic to check for public holidays (you can use a list of holidays)
    return True

def fetch_nse_tickers_with_names():
    try:
        # Check if the market is open
        if not is_market_open():
            print("Market is closed today. No data available.")
            return None
        
        # Fetch the latest price list from NSE
        price_list = get_price_list(datetime.now().date())
        
        # Extract relevant columns: SYMBOL (ticker) and NAME OF COMPANY
        tickers_with_names = price_list[['SYMBOL', 'NAME OF COMPANY']].drop_duplicates()
        
        # Sort by ticker
        tickers_with_names = tickers_with_names.sort_values(by='SYMBOL')
        
        return tickers_with_names
    except Exception as e:
        print(f"Error fetching NSE tickers: {e}")
        return None

def save_tickers_to_csv(tickers_with_names):
    if tickers_with_names is None or tickers_with_names.empty:
        print("No tickers to save.")
        return
    
    # Add a column for the date when the data was fetched
    tickers_with_names["Date_Fetched"] = datetime.now().strftime("%Y-%m-%d")
    
    # Create a filename with a date stamp
    filename = f"nse_tickers_with_names_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # Save the DataFrame to a CSV file
    tickers_with_names.to_csv(filename, index=False)
    print(f"Tickers with company names saved to {filename}")

def main():
    print("Fetching NSE stock tickers with company names...")
    tickers_with_names = fetch_nse_tickers_with_names()
    
    if tickers_with_names is not None and not tickers_with_names.empty:
        print(f"Total NSE stock tickers found: {len(tickers_with_names)}")
        save_tickers_to_csv(tickers_with_names)
    else:
        print("No tickers found or an error occurred.")

if __name__ == "__main__":
    main()