import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta, timezone
import warnings
from utils import download_csv, date_to_unix_timestamp
from utils import get_close_price, create_combined_df, multiply_columns
from utils import get_price_feed, usd_volume
from utils import MONTH_DIR


download_csv('algorand', 'usd')
start_date = '2025-08-01'
end_date = '2025-08-31'
ticker = "AFNUSD=X" #HAFN

stables_dfs = {}
stables_ids = {'usdc': 31566704, 'usdt': 312769,
              'eurs': 227855942,'xusd':760037151}

for stablecoin, stables_id in stables_ids.items():
    stables_dfs[stablecoin] = get_close_price(start_date, end_date, stables_id)

asas_dfs = {}
asas_ids = {
    'xalgo': 1134696561,
    'ora': 1284444444,
    'talgo': 2537013734,
    'vote': 452399768,
    'alpha': 2726252423,
    'gobtc': 386192725,
    'sparky': 3054226103,
    'tiny': 2200000000,
    'opul': 287867876,
    'finite': 400593267,
    'pow': 2994233666,
    'goeth': 386195940,
    'niko': 1265975021,
    'coop': 796425061,
    'compx': 1732165149,
    'monko': 2494786278,
    'avoi': 2320775407,
    'vest': 700965019,
    'gonna': 2582294183,
    'golddao': 1241945177
}


for asa, asa_id in asas_ids.items():
    asas_dfs[asa] = get_close_price(start_date, end_date, asa_id)


stables_final_df = create_combined_df(stables_dfs) 
asas_final_df = create_combined_df(asas_dfs)

algo_price = pd.read_csv(f'{MONTH_DIR}/algorand_historical_data.csv')
algo_price['snapped_at'] = pd.to_datetime(algo_price['snapped_at']).dt.date

stables_volumes = pd.read_csv(f'{MONTH_DIR}/stables.csv')
stables_volumes['dt'] = pd.to_datetime(stables_volumes['dt'])

asa_volumes = pd.read_csv(f'{MONTH_DIR}/asa_volumes.csv')
asa_volumes['dt'] = pd.to_datetime(asa_volumes['dt'])

algo = pd.read_csv(f'{MONTH_DIR}/algo_movements.csv')
algo['dt'] = pd.to_datetime(algo['dt']).dt.date
algo.rename(columns={'dt': 'date'}, inplace=True)

asa_algos = multiply_columns(asa_volumes, asas_final_df)
stables_algos = multiply_columns(stables_volumes, stables_final_df)


asa_algos['algo_vol'] = asa_algos[asa_algos.columns.values[1:]].sum(axis=1)
stables_algos['algo_vol'] = stables_algos[stables_algos.columns.values[1:]].sum(axis=1)

asa_algos['date'] = pd.to_datetime(asa_algos['date']).dt.date
stables_algos['date'] = pd.to_datetime(stables_algos['date']).dt.date

algo_usd = usd_volume(algo, algo_price)
asa_usd = usd_volume(asa_algos, algo_price)
stables_usd = usd_volume(stables_algos, algo_price)

algo_usd.to_csv(f'{MONTH_DIR}/Results/algo_usd.csv', index=False)
asa_usd.to_csv(f'{MONTH_DIR}/Results/asa_final_volumes.csv', index=False)
stables_usd.to_csv(f'{MONTH_DIR}/Results/stables_final_volumes.csv', index=False)


month_data = get_price_feed(ticker, start_date, end_date)
month_data.to_csv(f'{MONTH_DIR}/Results/HAFN.csv')
