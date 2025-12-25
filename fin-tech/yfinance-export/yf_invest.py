import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Function to get historical data for a stock
def get_historical_data(stock_name, years):
    try:
        # Calculate the start date based on the number of years
        end_date = datetime.now().date()
        start_date = (end_date - timedelta(days=365 * years)).strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')

        # Fetch historical data for the stock using yfinance
        stock_data = yf.download(
            tickers=stock_name,
            start=start_date,
            end=end_date,
            interval='1d'  # Daily data
        )

        return stock_data
    except Exception as e:
        print(f"Error fetching data for {stock_name}: {e}")
        return None

# Function to save data to CSV
def save_to_csv(data, filename):
    if data is not None:
        data.to_csv(filename)
        print(f"Data saved to {filename}")
    else:
        print("No data to save.")

# Main function
def main():
    # Get user inputs
    stock_name = input("Enter the stock name (e.g., AAPL for Apple): ").strip()
    years = int(input("Enter the number of years of historical data you want: ").strip())

    # Fetch historical data
    stock_data = get_historical_data(stock_name, years)

    # Save data to CSV
    save_to_csv(stock_data, f"{stock_name}_daily_data.csv")

# Run the script
if __name__ == "__main__":
    main()