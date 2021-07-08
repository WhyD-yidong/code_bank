import time
import pyupbit
import datetime
import requests
import operator

access = "uSzcamUv5xrwb2x89b8vNgQySU9dVrR0hGEfLkTM"
secret = "qwHiBK2448mmTxYxXB3pmtDfXpbnt0xqj1ckrtE4"

BUY = 0
SELL = 1
ratio = 0.01
crypto_cnt = 30
min_krw = 5000
Trading_start = False
state = BUY
buy_at_now = 1
getting_price = 0

crypto = []
crypto_krw = []
crypto_acc = []
list = []
sorted_list = []
trading_limit_price = 100000000 #1억
ref_price = []
get_price = []
sell_price = []
slope = []

buy_price = 0

idx = 0
index = 0

def get_percent(src1, src2):
    p = (src1 - src2) / src1 * 100
    return p


def get_acc_trade_price(ticker):
    url = "https://api.upbit.com/v1/candles/days"
    querystring = {"market": ticker, "count": "1"}
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()[0]['candle_acc_trade_price']


def get_ticker():
    idx = 0
    list = []
    volume = []
    crypto_list = []
    crypto_sorted_list = []

    tickers = pyupbit.get_tickers(fiat='KRW')
    for idx in tickers:
        list.append(idx)
        volume.append(get_acc_trade_price(idx))
        time.sleep(0.1)

    for idx in range(len(list)):
        crypto_list.append([list[idx], volume[idx]])

    crypto_sorted_list = sorted(crypto_list, key=operator.itemgetter(1), reverse=True)

    list_krw = []

    for idx in range(len(list)):
        list_krw.append(crypto_sorted_list[idx][0])
        if idx >= 100:
            break

    list = []

    for idx in range(100):

        string = list_krw[idx]
        list.append(string[4:])

    return list_krw, list


def get_slope(ticker):
    # """MA5 * 1%fh  매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    ma2 = df['close'].rolling(window=2).mean()
    if ma2[-3] >= ma2[-2]:
        return 0
    elif ma2[-3] < ma2[-2]:
        return 1


def get_ref_price(ticker):
    # """MA5 * 1%fh  매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    ma5 = df['close'].rolling(window=5).mean()
    last_ma5 = ma5[-2]
    return last_ma5


def get_balance(ticker):
    # """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
    return 0.0


def get_buy_price(ticker):
    # """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])
    return 0.0


def get_current_price(ticker):
    # """현재가 조회"""
    return  pyupbit.get_current_price(ticker)


def forced_sell(crypto, balance):
    upbit.sell_market_order(crypto, balance)


def crypto_print(*str):
    #print(str)
    return 0


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")


# 자동매매 시작
while True:
    try:

        now = datetime.datetime.now()

        if Trading_start == False:
            ref_price = []
            get_price = []
            sell_price = []
            slope = []
            buy_price = 0
            index = 0

            crypto_krw, crypto = get_ticker()

            for cnt in range(crypto_cnt):
                price = get_ref_price(crypto_krw[cnt]) #ms5 ref
                slope_val = get_slope(crypto_krw[cnt])
                balance = get_balance(crypto[cnt])
                crypto_print(cnt, crypto_krw[cnt])

                ref_price.append(price)
                get_price.append(price)
                sell_price.append(price)
                slope.append(slope_val)
                time.sleep(0.1)

            for cnt in range(100):
                buy_price = get_buy_price(crypto[cnt]) #매수가
                balance = get_balance(crypto[cnt])
                if buy_price * balance > min_krw:
                    print("sell state", cnt)
                    if cnt < crypto_cnt:
                        state = SELL
                        index = cnt

                        if sell_price[cnt] < buy_price * (1 - ratio):
                            sell_price[cnt] = buy_price * (1 - ratio)
                    else:
                        forced_sell(crypto_krw[cnt], balance)
                    break

            Trading_start = True
        else:
            krw = get_balance("KRW")
            total_balance = upbit.get_amount('ALL') + krw

            if state is BUY:

                cur_price = get_current_price(crypto_krw[idx])

                if get_balance("KRW") < min_krw:   #pass SELL state
                    state = SELL

                if total_balance > trading_limit_price:
                    krw_sub = krw / 10
                else:
                    krw_sub = krw

                if get_price[idx] < cur_price and slope[idx] == 1:
                    if krw > min_krw:
                        upbit.buy_market_order(crypto_krw[idx], krw_sub * 0.9995)

                        crypto_print(crypto_krw[idx], get_price[idx], cur_price, idx, "Buy in", now.hour, now.minute,
                                     now.second)
                        if get_balance("KRW") < min_krw:
                            state = SELL
                            index = idx
                            sell_price[index] = cur_price * (1 - ratio)
                            buy_price = cur_price
                            buy_at_now = 1
                        else:
                            idx -= 1

                    else:
                        crypto_print(crypto_krw[idx],idx, "T_P:", get_price[idx], "C_P", cur_price, krw, idx,
                                     "No resource", now.hour, now.minute, now.second)
                else:
                    crypto_print(crypto_krw[idx],idx, "T_P:", get_price[idx], "C_P:", cur_price, "No satisfy price", format(get_percent(get_price[idx],cur_price), ".2f"),  now.hour, now.minute, now.second)
                    # please update go to current price under target price during buy.#

                idx += 1

                if idx >= crypto_cnt:
                    idx = 0

            elif state is SELL:

                cur_price = get_current_price(crypto_krw[index])
                cur_balance = get_balance(crypto[index])

                if cur_balance < (min_krw / cur_price):  #pass BUY state
                    state = BUY

                if total_balance > trading_limit_price:
                    sub_balance = cur_balance / 10
                else:
                    sub_balance = cur_balance

                if sell_price[index] > cur_price:
                    upbit.sell_market_order(crypto_krw[index], sub_balance)
                    if get_balance(crypto[index]) < (min_krw / cur_price):
                        state = BUY
                        if buy_at_now == 1:
                            get_price[index] = buy_price * (1 + ratio)

                        crypto_print(crypto_krw[index], sell_price[index], cur_price, "Sell out", now.hour, now.minute, now.second)

                else:
                    crypto_print(crypto_krw[index], "T_P:", sell_price[index], "C_P:", cur_price, "Over T_P", format(get_percent(sell_price[index], cur_price), ".2f"),  now.hour, now.minute, now.second)
                    # please update go to current price over target price during sell.#

        if now.minute == 00 and now.second >= 00 and now.second <= 19:
            if sell_price[index] < buy_price:
                sell_price[index] = buy_price

        if now.hour == 9 and now.minute == 00 and now.second >= 00 and now.second <= 19:
            buy_at_now = 0
            Trading_start = False
            idx = 0

        crypto_print("===================================================")
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)