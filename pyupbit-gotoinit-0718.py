import time
import pyupbit
import datetime
import requests
import operator

access = "uSzcamUv5xrwb2x89b8vNgQySU9dVrR0hGEfLkTM"
secret = "qwHiBK2448mmTxYxXB3pmtDfXpbnt0xqj1ckrtE4"

BUY = 0
SELL = 1
price_lim = 0.01
ratio = 0.03
crypto_cnt = 30
holding_cnt = 5
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

buy_price = 0

idx = 0

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
    df = pyupbit.get_ohlcv(ticker, interval="minute30", count=7)
    close2 = df['close']
    ma5 = df['close'].rolling(window=5).mean()
    ma2 = df['close'].rolling(window=2).mean()
    if ma2[-2] > ma5[-2] and close2[-2] < close2[-1]:
        return 1
    else:
        return 0


def get_slope2(ticker):
    df = pyupbit.get_ohlcv(ticker, count=3)
    close2 = df['close']
    if close2[-2] < close2[-1]:
        return 1
    else:
        return 0


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
    return pyupbit.get_current_price(ticker)


def forced_sell(crypto, balance):
    upbit.sell_market_order(crypto, balance)
    #return 0


def update_sell_price(index, cur_price):
    temp_price = 0
    buy_price = get_buy_price(crypto[index])
    if cur_price > buy_price:
        temp_price = cur_price * (1 - ratio)
        if sell_price[index] < temp_price:
            sell_price[index] = temp_price
    #print("sell_price2:", index, sell_price[index])
    return 0


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

            buy_price = 0

            crypto_krw, crypto = get_ticker()           #get 100 item sorted by acc_trading price
            for cnt in range(crypto_cnt):
                price = get_ref_price(crypto_krw[cnt])  #get ms5 ref
                #balance = get_balance(crypto[cnt])
                crypto_print(cnt, crypto_krw[cnt])

                ref_price.append(price)
                get_price.append(price)
                sell_price.append(price)

                time.sleep(0.1)

            for cnt in range(100):  #sellout out of
                buy_price = get_buy_price(crypto[cnt])  #매수가
                balance = get_balance(crypto[cnt])
                cur_price = get_current_price(crypto_krw[cnt])
                if buy_price * balance > min_krw:
                    print("sell state", cnt)
                    if cnt < crypto_cnt:
                        if cur_price > buy_price:
                            if sell_price[cnt] < buy_price:
                                sell_price[cnt] = buy_price
                        else:
                            sell_price[cnt] = buy_price * (1 - ratio)
                    else:
                        forced_sell(crypto_krw[cnt], balance)

            Trading_start = True
        else:
            krw = get_balance("KRW")
            total_balance = upbit.get_amount('ALL') + krw
            balance_portion = total_balance / holding_cnt

            cur_price = get_current_price(crypto_krw[idx])
            cur_balance = get_balance(crypto[idx])
            balance_on_krw = cur_balance * cur_price

            # if total_balance > trading_limit_price:
            #     krw_sub = krw / 10
            #     sub_balance = cur_balance / 10
            # else:
            #     krw_sub = krw
            #     sub_balance = cur_balance

            if get_price[idx] < cur_price and (get_price[idx] * (1+price_lim)) > cur_price and get_slope(crypto_krw[idx]) == 1 and get_slope2(crypto_krw[idx]) == 1:
                if (balance_portion - balance_on_krw) > min_krw and krw > min_krw:
                    upbit.buy_market_order(crypto_krw[idx], min(balance_portion - balance_on_krw, krw) * 0.9995)
                    sell_price[idx] = get_buy_price(crypto[idx]) * (1 - ratio)
                    crypto_print(idx, crypto_krw[idx], "Buy in", get_price[idx], cur_price, now.hour, now.minute, now.second)
                else:
                    crypto_print(idx, crypto_krw[idx], "No resource", get_price[idx], cur_price, now.hour, now.minute, now.second)
            elif sell_price[idx] > cur_price:
                if cur_balance > (min_krw / cur_price):
                    upbit.sell_market_order(crypto_krw[idx], cur_balance)
                    crypto_print(idx, crypto_krw[idx], "Sell out", sell_price[idx], cur_price, now.hour, now.minute, now.second)
                else:
                    crypto_print(idx, crypto_krw[idx], "No Balance", sell_price[idx], cur_price, now.hour, now.minute, now.second)
            else:
                crypto_print(idx, crypto_krw[idx], sell_price[idx], cur_price, "No satisfy Condition", now.hour, now.minute, now.second)
            update_sell_price(idx, cur_price)

        idx += 1
        if idx >= crypto_cnt:
            idx = 0

        if now.hour == 9 and now.minute == 30 and now.second >= 00 and now.second <= 19:
            Trading_start = False
            idx = 0

        crypto_print("===================================================")
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)