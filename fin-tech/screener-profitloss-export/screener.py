import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to fetch financial data from Screener.com
def fetch_financial_data(ticker):
    url = f"https://www.screener.in/company/{ticker}/consolidated/#profit-loss"
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes (4xx or 5xx)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the Profit & Loss table
        table = soup.find("table", {"class": "data-table"})
        if not table:
            print("Error: Profit & Loss table not found on the page.")
            return None

        # Extract headers (years and TTM)
        headers = [th.text.strip() for th in table.find_all("th")]
        headers = [header for header in headers if header]  # Remove empty headers

        # Extract rows (financial metrics)
        financial_data = {}
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 0:
                continue  # Skip header rows

            # Extract the metric name (first column)
            metric = cols[0].text.strip()

            # Extract values for each year/TTM
            values = [col.text.strip() for col in cols[1:]]
            financial_data[metric] = values

        # Create a DataFrame
        df = pd.DataFrame(financial_data, index=headers)
        return df

    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None

# Main script
if __name__ == "__main__":
    # Prompt user for inputs
    ticker = input("Enter the NSE ticker symbol (e.g., RELIANCE): ")

    # Fetch financial data
    print(f"Fetching financial data for {ticker}...")
    financial_data = fetch_financial_data(ticker)

    if financial_data is not None:
        # Save to CSV
        output_file = f"{ticker}_profit_loss.csv"
        financial_data.to_csv(output_file)
        print(f"Financial data saved to {output_file}!")
    else:
        print("Failed to fetch financial data. Please check your inputs and try again.")