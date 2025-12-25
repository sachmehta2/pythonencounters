import requests
import pandas as pd
from datetime import datetime

# Function to fetch income statement data
def fetch_income_statement(symbol, api_key):
    # Alpha Vantage API endpoint for income statement
    url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={api_key}"

    try:
        # Send a GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes (4xx or 5xx)

        # Parse the JSON response
        data = response.json()

        # Check if the API returned an error message
        if "Error Message" in data:
            print(f"Error for {symbol}: {data['Error Message']}")
            return None
        if "Note" in data:  # API rate limit or other issues
            print(f"API Limit Reached for {symbol}: {data['Note']}")
            return None
        if "annualReports" not in data:
            print(f"Error: No income statement data found for {symbol}.")
            return None

        # Extract annual reports
        annual_reports = data["annualReports"]

        # Add the ticker symbol to each report
        for report in annual_reports:
            report["Ticker"] = symbol

        return annual_reports

    except requests.exceptions.RequestException as e:
        print(f"Network Error for {symbol}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error for {symbol}: {e}")
        return None

# Function to save combined data to CSV
def save_to_csv(data, output_file):
    # Convert the combined data to a DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Combined income statement data saved to {output_file}!")

# Main script
if __name__ == "__main__":
    # Prompt user for inputs
    ticker_file = input("Enter the path to the ticker file (e.g., tickers.txt): ")
    api_key = input("Enter your Alpha Vantage API key: ")

    # Read tickers from the file and strip whitespace
    with open(ticker_file, "r") as file:
        tickers = [line.strip() for line in file.readlines()]

    # Fetch income statement data for all tickers
    combined_data = []
    for ticker in tickers:
        print(f"Fetching income statement data for {ticker}...")
        income_statement_data = fetch_income_statement(ticker, api_key)
        if income_statement_data:
            combined_data.extend(income_statement_data)

    if combined_data:
        # Generate the output file name
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"combined_income_statements_{current_time}.csv"

        # Save combined data to CSV
        save_to_csv(combined_data, output_file)
    else:
        print("No data fetched. Please check your inputs and try again.")