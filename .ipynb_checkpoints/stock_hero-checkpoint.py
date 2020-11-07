# imports
import panel as pn
pn.extension('plotly')

import pandas as pd
import alpaca_trade_api as tradeapi
import numpy as np
import requests
import json
import os

from datetime import date, timedelta
from MCForecastTools import MCSimulation
from dotenv import load_dotenv
from newsapi import NewsApiClient

import matplotlib.pyplot as plt
import plotly.express as px
import hvplot.pandas

# Set APIs keys
load_dotenv()
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")
news_api_key = os.getenv("NEWS_API_KEY")

#Getting ticker to evaluate 
tickers = input("Enter the stock to evaluate: ") 

def get_symbol(symbol):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)

    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']
company = get_symbol(f"{tickers}")

print(f"You entered {tickers}: {company}. Let's evaluate it...") 

today = date.today()
previous_month_date = date.today() - timedelta(30)
newsapi = NewsApiClient(api_key=f"{news_api_key}")
all_articles = newsapi.get_everything(q=f"{company}",
                                          from_param=today,
                                          to=previous_month_date,
                                          language='en',
                                          sort_by='relevancy',
                                          page_size=5,
                                          page=1
                                         )
article_title = all_articles["articles"][0]["title"]
print(article_title)
article_link = all_articles["articles"][0]["url"]
print(article_link)
print("\n")

article_title = all_articles["articles"][1]["title"]
print(article_title)
article_link = all_articles["articles"][1]["url"]
print(article_link)
print("\n")

article_title = all_articles["articles"][2]["title"]
print(article_title)
article_link = all_articles["articles"][2]["url"]
print(article_link)
print("\n")

article_title = all_articles["articles"][3]["title"]
print(article_title)
article_link= all_articles["articles"][3]["url"]
print(article_link)
print("\n")

article_title = all_articles["articles"][4]["title"]
print(article_title)
article_link= all_articles["articles"][4]["url"]
print(article_link)
print("\n")

api = tradeapi.REST(
    alpaca_api_key,
    alpaca_secret_key,
    api_version = "v2"
)
timeframe ='1D'
start_date = pd.Timestamp("2011-01-01", tz="America/New_York").isoformat()
end_date = pd.Timestamp(today, tz="America/New_York").isoformat()
df_ticker = api.get_barset(
    tickers,
    timeframe,
    start=start_date,
    end=end_date
).df
MC_ticker = MCSimulation(
    portfolio_data = df_ticker,
    weights = [1],
    num_simulation = 1000,
    num_trading_days = 252*5
)
MC_ticker.calc_cumulative_return()
ticker_tbl = MC_ticker.summarize_cumulative_return()

# Set initial investment
initial_investment = 1

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $60,000
ci_lower = round(ticker_tbl[8]*initial_investment,2)
ci_upper = round(ticker_tbl[9]*initial_investment,2)

# Print results
print(f"There is a 95% chance that a dollar invested in {company}"
      f" over the next 5 years will end within in the range of"
      f" ${('{:,}'.format(ci_lower))} and ${('{:,}'.format(ci_upper))}.")

df_spy = api.get_barset(
    'SPY',
    timeframe,
    start=start_date,
    end=end_date
).df
df_dia = api.get_barset(
    'DIA',
    timeframe,
    start=start_date,
    end=end_date
).df
df_compare = pd.concat([df_ticker, df_spy, df_dia], axis="columns", join="inner")
df_close = df_compare.xs('close',level=1,axis=1)
df_return = df_close.pct_change()
df_return.dropna(inplace=True)
df_cumreturn = (1+ df_return).cumprod()-1
df_cumreturn.hvplot(
    title="Historical cumulative returns",
    xlabel="Year",
    figsize=(20,10)
)

df_correlation = df_return.corr()
df_correlation.head()

df_sharpe = (df_return.mean() * 252) / (df_return.std() * np.sqrt(252))
df_sharpe.hvplot(
    kind="bar",
    title=f"Sharpe ratio for {company} compared to SPY and DIA"
)
