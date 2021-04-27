import time
import pyupbit
import datetime


access = "uSzcamUv5xrwb2x89b8vNgQySU9dVrR0hGEfLkTM"
secret = "qwHiBK2448mmTxYxXB3pmtDfXpbnt0xqj1ckrtE4"
ratio = 0.0005

def get_buy_target_price(ticker):
   #"""MA5 * 1%fh  매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    ma5 = df['close'].rolling(window=5).mean()
    last_ma5 = ma5[-2]
    up_range = last_ma5 * (1+ratio)
    return up_range

def get_sell_target_price(ticker):
   #"""MA5 * 1%fh  매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    ma5 = df['close'].rolling(window=5).mean()
    last_ma5 = ma5[-2]
    down_range = last_ma5 * (1-ratio)
    return down_range

def get_start_time(ticker):
    #"""시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_balance(ticker):
    #"""잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0


def get_current_price(ticker):
    #"""현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        up_target_price = get_buy_target_price("KRW-BTC")
        down_target_price = get_sell_target_price("KRW-BTC")
        current_price = get_current_price("KRW-BTC")

        krw = get_balance("KRW")
        btc = get_balance("BTC")
        if up_target_price < current_price:
            print("Waiting buy", current_price, up_target_price, krw, btc)
            if krw > 5000:
                upbit.buy_market_order("KRW-BTC", krw*0.9995)
        elif down_target_price > current_price:
            print("Waiting sell", current_price, down_target_price, krw, btc)
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        else:
            #print("Waiting out of range", current_price, up_target_price, down_target_price)
            print("Waiting out of range")
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)
