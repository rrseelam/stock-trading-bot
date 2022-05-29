import math
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
import yfinance as yf
import talib
import pandas as pd
import datetime


load_dotenv()

BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

api = tradeapi.REST(key_id=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY,
                    base_url=BASE_URL, api_version='v2')

clock = api.get_clock()


def get_data(stock_ticker: str):
    stock = yf.Ticker(stock_ticker)
    data = stock.history(period="1y", interval="1d")
    return data


def buy(stock_ticker: str):
    # determine how many shares to buy
    cash = api.get_account().cash
    stock_price = api.get_latest_trade(stock_ticker).price
    amountToBuy = math.floor(int(cash)/stock_price)
    print("Buy: " + amountToBuy)
    # place order
    api.submit_order(stock_ticker, amountToBuy, "buy", "market", "day")


def sell(stock_ticker: str):
    # determine how many shares to sell and close position
    amountToSell = api.get_position(stock_ticker).qty
    stock_price = api.get_latest_trade(stock_ticker).price
    print("Sell: " + amountToSell)
    api.close_position(stock_ticker)


def SMA(values, n):
    """
    Returns simple moving average of (values) for the past (n) days
    """
    close = pd.Series(values)
    return talib.SMA(close, timeperiod=n)


def cross(series1, series2):
    # checks if the moving averages have crossed
    if (series1[-2] < series2[-2] and series1[-1] > series2[-1]):
        return True
    else:
        return False


def main():
    while True:
        # gets the time and checks if the market is open and if it is 11am
        time = datetime.datetime.now()
        if time.strftime("%H") == "11" and time.strftime("%M") == "0":
            if clock.is_open:
                # gets data for the stock and checks if the moving averages have crossed
                data = get_data("VOO")
                smallSMA = SMA(data, 5)
                bigSMA = SMA(data, 15)
                if cross(smallSMA, bigSMA):
                    buy("VOO")
                elif cross(bigSMA, smallSMA):
                    sell("VOO")


if __name__ == '__main__':
    main()
