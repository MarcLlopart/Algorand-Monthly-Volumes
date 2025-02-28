import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta, timezone
import warnings

MONTH_DIR = 'Feb 2025'

def download_csv(coin_id, currency):
    """
    This function downloads the data from Coingecko with the usd pair.
    Inputs:
        - coin_id: the name of the crypto we are getting the data
        - currency: by default it is the usd
    Output:
        - This function simply stores under raw_data directory a file
        from coingecko with all historic data available
    """
    # Construct the URL
    base_url = "https://www.coingecko.com"
    csv_path = f"/price_charts/export/{coin_id}/{currency}.csv"
    full_url = base_url + csv_path

    # Download the CSV
    response = requests.get(full_url)
    if response.status_code == 200:
        file_name = f"{MONTH_DIR}/{coin_id}_historical_data.csv"
        with open(file_name, "wb") as file:
            file.write(response.content)

    else:
        print(f"Failed to download CSV for {coin_id}.")

def date_to_unix_timestamp(start_date_str, end_date_str):
  """
  Converts start and end dates in YYYY-MM-DD format to Unix timestamps.

  Args:
    start_date_str: Start date string in YYYY-MM-DD format.
    end_date_str: End date string in YYYY-MM-DD format.

  Returns:
    A tuple containing the start and end Unix timestamps.
  """

  start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
  end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1) - timedelta(seconds=1) 

  start_timestamp = int(start_date.timestamp())
  end_timestamp = int(end_date.timestamp())

  return start_timestamp, end_timestamp

def get_close_price(start_date, end_date, asset_id):
    """
    Fetches an asset historical data from the API for the given interval.
    
    Args:
        start_timestamp: start unix timestamp
        end_timestamp: end unix timestamp

    Returns:
        pd.DataFrame: Dataframe containing the fetched data in daily intervals.
    """
    start_unix, end_unix = date_to_unix_timestamp(start_date, end_date)

    price_feed = f'https://indexer.vestige.fi/assets/{asset_id}/candles?network_id=0&interval=86400&start={start_unix}&end={end_unix}&denominating_asset_id=0&volume_in_denominating_asset=false'

    response = requests.get(price_feed)
    data = response.json()
    df = pd.DataFrame(data)
    return df

def create_combined_df(dataframes):
  """
  Creates a single DataFrame with 'date' as the index and 
  'close' columns named after the stablecoin keys.

  Args:
    dataframes: A dictionary where keys are stablecoin names 
                and values are the corresponding DataFrames.

  Returns:
    A pandas DataFrame with the combined data.
  """

  combined_df = pd.DataFrame()

  for asset, df in dataframes.items():
    df['date'] = pd.to_datetime(df['timestamp'], unit='s') 
    df.set_index('date', inplace=True) 
    df.rename(columns={'close': asset}, inplace=True) 
    combined_df = combined_df.join(df[asset], how='outer') 

  return combined_df

def multiply_columns(df1, df2):
  """
  Joins price and volume dataframes to convert into ALGO volumes

  Args:
    df1: Volumes Dataframe in native Currency
    df2: Asset/ALGO Price DataFrame.

  Returns:
    A merged DataFrame with ALGO Volumes
  """

  # Merge DataFrames on 'dt' and 'date'
  merged_df = df1.merge(df2, left_on='dt', right_on='date', suffixes=('_df1', '_df2'))

  # Calculate product of corresponding columns
  columns_to_multiply = df1.columns.values[1:]
  for col in columns_to_multiply:
      merged_df[col] = merged_df[col + '_df1'] * merged_df[col + '_df2']

  # Drop unnecessary columns
  merged_df.drop(columns=[col + '_df1' for col in columns_to_multiply] + 
                  [col + '_df2' for col in columns_to_multiply], 
             inplace=True)

  # Rename 'dt' column to 'date'
  merged_df.rename(columns={'dt': 'date'}, inplace=True)

  return merged_df

def get_price_feed(ticker, start_date, end_date):
  """
  Fetches the price feed for the specified ticker for December 2024 
  using the yfinance library.

  Args:
    ticker: The ticker symbol (e.g., "AFNUSD=X").

  Returns:
    A pandas DataFrame containing the historical data for the specified period.
  """

  try:
    # Define start and end dates, consider forex does not operate 24/7
    start_date = start_date
    end_date = end_date

    # Download historical data using yfinance
    data = yf.download(ticker, start=start_date, end=end_date)
    return data
  except Exception as e:
    print(f"Error fetching data for {ticker}: {e}")
    return None

def usd_volume(algo_volumes, algo_price):
  """
  Joins volumes and algo price dataframes to convert into USD volume

  Args:
    df1: Volumes Dataframe in ALGO
    df2: ALGO/USD Price DataFrame.

  Returns:
    A merged DataFrame with ALGO Volumes
  """

    # Merge DataFrames on 'dt' and 'date'
  merged_df = algo_volumes.merge(algo_price[['snapped_at', 'price']], left_on='date', right_on='snapped_at')

  merged_df.drop('snapped_at', axis=1, inplace=True)
  # Calculate product of corresponding columns
  merged_df['usd_vol'] = merged_df['algo_vol']*merged_df['price']

  # Rename 'dt' column to 'date'
  #merged_df.rename(columns={'dt': 'date'}, inplace=True)

  return merged_df