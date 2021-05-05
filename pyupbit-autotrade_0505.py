import time
import pyupbit
import datetime

access = "uSzcamUv5xrwb2x89b8vNgQySU9dVrR0hGEfLkTM"
secret = "qwHiBK2448mmTxYxXB3pmtDfXpbnt0xqj1ckrtE4"
ratio = 0.0005
total_cnt = 4
total_balance = 0
min_krw = 5000


def get_ref_price(ticker):
    # """MA5 * 1%fh  매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    ma5 = df['close'].rolling(window=5).mean()
    last_ma5 = ma5[-2]
    return last_ma5


def get_buy_target_price(ticker):
    return get_ref_price(ticker) * (1 + ratio)


def get_sell_target_price(ticker):
    return get_ref_price(ticker) * (1 - ratio)


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
                return 0.0


def get_current_price(ticker):
    #"""현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        BTC_ref_price = get_ref_price("KRW-BTC")
        ETH_ref_price = get_ref_price("KRW-ETH")
        XRP_ref_price = get_ref_price("KRW-XRP")
        DOGE_ref_price = get_ref_price("KRW-DOGE")

        print("BTC==========", BTC_ref_price, get_buy_target_price("KRW-BTC"), get_sell_target_price("KRW-BTC"))
        print("ETH==========", ETH_ref_price, get_buy_target_price("KRW-ETH"), get_sell_target_price("KRW-ETH"))
        print("XRP==========", XRP_ref_price, get_buy_target_price("KRW-XRP"), get_sell_target_price("KRW-XRP"))
        print("DOGE=========", DOGE_ref_price, get_buy_target_price("KRW-DOGE"), get_sell_target_price("KRW-DOGE"))

        BTC_cur_price = get_current_price("KRW-BTC")
        ETH_cur_price = get_current_price("KRW-ETH")
        XRP_cur_price = get_current_price("KRW-XRP")
        DOGE_cur_price = get_current_price("KRW-DOGE")
        print("current price:", BTC_cur_price, ETH_cur_price, XRP_cur_price, DOGE_cur_price)

        btc = get_balance("BTC")
        eth = get_balance("ETH")
        xrp = get_balance("XRP")
        doge = get_balance("DOGE")
        krw = get_balance("KRW")
        print("current blance:", btc, eth, xrp, krw)

        btc_krw = btc * BTC_cur_price
        eth_krw = eth * ETH_cur_price
        xrp_krw = xrp * XRP_cur_price
        doge_krw = doge * DOGE_cur_price

        total_balance = btc_krw + eth_krw + xrp_krw + doge_krw + krw
        balance_portion = total_balance / total_cnt
        print("total", total_balance, balance_portion)

        if get_buy_target_price("KRW-BTC") < BTC_cur_price:
            if btc_krw < balance_portion and krw > min_krw:
                print("within condition for BTC buying")
                #upbit.buy_market_order("KRW-BTC", (balance_portion-btc_krw)*0.9995)
            else:
                print("beside condition for BTC buying")
        elif get_sell_target_price("KRW-BTC") > BTC_cur_price:
            if btc > (min_krw / BTC_cur_price):
                print("within condition for BTC selling")
                #upbit.sell_market_order("KRW-BTC", btc*0.9995)
            else:
                print("beside condition for BTC selling")

        if get_buy_target_price("KRW-ETH") < ETH_cur_price:
            if eth_krw < balance_portion and krw > min_krw:
                print("within condition for ETH buying")
                #upbit.buy_market_order("KRW-ETH", (balance_portion-eth_krw)*0.9995)
            else:
                print("beside condition for ETH buying")
        elif get_sell_target_price("KRW-ETH") > ETH_cur_price:
            if eth > (min_krw / ETH_cur_price):
                print("within condition for ETH selling")
                #upbit.sell_market_order("KRW-ETH", eth*0.9995)
            else:
                print("beside condition for ETH selling")

        if get_buy_target_price("KRW-XRP") < XRP_cur_price:
            if xrp_krw < balance_portion and krw > min_krw:
                print("within condition for XRP buying")
                #upbit.buy_market_order("KRW-XRP", (balance_portion-xrp_krw)*0.9995)
            else:
                print("beside condition for XRP buying")
        elif get_sell_target_price("KRW-XRP") > XRP_cur_price:
            if xrp > (min_krw / XRP_cur_price):
                print("within condition for XRP selling")
                #upbit.sell_market_order("KRW-XRP", xrp*0.9995)
            else:
                print("beside condition for XRP selling")
                
        if get_buy_target_price("KRW-DOGE") < DOGE_cur_price:
            if doge_krw < balance_portion and krw > min_krw:
                print("within condition for DOGE buying")
                #upbit.buy_market_order("KRW-XRP", (balance_portion-doge_krw)*0.9995)
            else:
                print("beside condition for DOGE buying")
        elif get_sell_target_price("KRW-DOGE") > DOGE_cur_price:
            if xrp > (min_krw / DOGE_cur_price):
                print("within condition for DOGE selling")
                #upbit.sell_market_order("KRW-XRP", doge*0.9995)
            else:
                print("beside condition for DOGE selling")                
        print("===========================================================================")
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)
