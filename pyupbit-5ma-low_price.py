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
ratio = 0.05
crypto_cnt = 109
holding_cnt = 5
min_krw = 5000
Trading_start = True
state = BUY
buy_at_now = 1
getting_price = 0
max_price = []

crypto = []
crypto_krw = []
crypto_acc = []
list = []
sorted_list = []
trading_limit_price = 100000000 #1억
ref_price = []
hold = []


buy_price = 0

idx = 0

def get_percent(src1, src2):
    p = (src1 - src2) / src1 * 100
    return p


def get_acc_trade_price(ticker):
    #url = "https://api.upbit.com/v1/candles/days"
    #querystring = {"market": ticker, "count": "1"}
    #headers = {"Accept": "application/json"}
    #response = requests.request("GET", url, headers=headers, params=querystring)
    #return response.json()[0]['candle_acc_trade_price']
    day = pyupbit.get_ohlcv(ticker, count=2)
    value = day['value']
    return value[-2]


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
        print("=", idx)
        time.sleep(0.05)

    for idx in range(len(list)):
        crypto_list.append([list[idx], volume[idx]])

    crypto_sorted_list = sorted(crypto_list, key=operator.itemgetter(1), reverse=True)

    list_krw = []

    for idx in range(len(list)):
        list_krw.append(crypto_sorted_list[idx][0])

    list = []

    for idx in range(len(list_krw)):

        string = list_krw[idx]
        list.append(string[4:])

    return list_krw, list


def get_price_condition(ticker):
    # """MA5 * 1%fh  매수 목표가 조회"""
    ref = 0
    result = 0
    df = pyupbit.get_ohlcv(ticker, count=22)
    df_close = df['close']
    if len(df_close) < 22:
        return 1, 0
    ma5 = df['close'].rolling(window=5).mean()
    ma10 = df['close'].rolling(window=10).mean()
    ma20 = df['close'].rolling(window=20).mean()

    if ((df_close[-3] < ma10[-2] and ma10[-2] < df_close[-2]) or (df_close[-3] < ma10[-1] and ma10[-1] < df_close[-2])) and (df_close[-2] < df_close[-3] * 1.3):
        result = 1
        ref = ma10[-2]
    elif ((df_close[-3] > ma10[-2] and ma10[-2] > df_close[-2]) or (ma10[-2] > df_close[-2] and ma10[-2] > df_close[-3])) and (ma20[-3] - ma20[-2] <= 0) :
        result = 2
        ref = ma10[-2]
    elif ((df_close[-3] > ma5[-2] and ma5[-2] > df_close[-2]) or (ma5[-2] > df_close[-2] and ma5[-2] > df_close[-3])) and (ma20[-3] - ma20[-2] > 0):
        result = 2
        ref = ma5[-2]
    else:
        result = 0
        ref = ma5[-2]
    return ref, result


def get_price_condition_curr(ticker):
    # """MA5 * 1%fh  매수 목표가 조회"""
    ref = 0
    result = 0
    df = pyupbit.get_ohlcv(ticker, count=22)
    df_close = df['close']
    if len(df_close) < 22:
        return 1, 0    
    ma5 = df['close'].rolling(window=5).mean()
    ma10 = df['close'].rolling(window=10).mean()
    ma20 = df['close'].rolling(window=20).mean()

    if (df_close[-2] < ma10[-1] and ma10[-1] < df_close[-1]) and (df_close[-1] < df_close[-2] * 1.3):
        result = 1
        ref = ma10[-1]
    elif (df_close[-2] > ma10[-1] and ma10[-1] > df_close[-1]) and (ma20[-2] - ma20[-1] <= 0):
        result = 2
        ref = ma10[-1]
    elif (df_close[-2] > ma5[-1] and ma5[-1] > df_close[-1]) and (ma20[-2] - ma20[-1] > 0):
        result = 2
        ref = ma5[-1]
    else:
        result = 0
        ref = ma5[-1]
    return ref, result



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
    #upbit.sell_market_order(crypto, balance)
    pass
    

def crypto_print(*str):
    print(str)
    #return 0


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:

        now = datetime.datetime.now()
        
        if now.hour == 9 and now.minute == 00 and (now.second >= 00 and now.second <=30):
            Trading_start = True
            idx = 0

        if Trading_start == True:
            Trading_start = False
            ref_price = []

            buy_price = 0
            count = 0


            print("== Get crypto list==")
            crypto_krw, crypto = get_ticker()           #get 100 item sorted by acc_trading price

            crypto_cnt = len(crypto_krw)
            hold = [0] * crypto_cnt
            max_price = [0] * crypto_cnt
            
            print("== Chk holding crypto ==")
            for cnt in range(crypto_cnt):  #sellout out of
                buy_price = get_buy_price(crypto[cnt])  #매수가
                balance = get_balance(crypto[cnt])
                cur_price = get_current_price(crypto_krw[cnt])
                if buy_price * balance > min_krw:
                    print("sell state", cnt)
                    if cnt < crypto_cnt:
                        hold[cnt] = 2
                    else:
                        forced_sell(crypto_krw[cnt], balance)
                else:
                    print("==",cnt)
                time.sleep(0.1)

            for cnt in range(crypto_cnt):
                price, result = get_price_condition(crypto_krw[cnt])  #get ms5 ref

                krw = get_balance("KRW")
                total_balance = upbit.get_amount('ALL') + krw
                balance_portion = total_balance / holding_cnt
                
                cur_price = get_current_price(crypto_krw[cnt])
                cur_balance = get_balance(crypto[cnt])
                balance_on_krw = cur_balance * cur_price
                ref_price.append(price)
                
                if (hold[cnt] == 1 or hold[cnt] == 2) and (result == 2 or result == 3):
                    if cur_balance > (min_krw / cur_price):
                        upbit.sell_market_order(crypto_krw[cnt], cur_balance)
                        hold[cnt] = 0
                        print("{0:2d}:{1}_{2}\t SELL OUT REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}".format(cnt, crypto_krw[cnt], hold[cnt], ref_price[cnt], cur_price, get_percent(ref_price[cnt], cur_price), now.hour, now.minute, now.second))
                else:
                    print("{0:2d}:{1}_{2}".format(cnt, crypto_krw[cnt], result))
                time.sleep(0.1)

            for cnt in range(crypto_cnt):
                price, result = get_price_condition(crypto_krw[cnt])  #get ms5 ref
                
                krw = get_balance("KRW")
                total_balance = upbit.get_amount('ALL') + krw
                balance_portion = total_balance / holding_cnt
                
                cur_price = get_current_price(crypto_krw[cnt])
                cur_balance = get_balance(crypto[cnt])
                balance_on_krw = cur_balance * cur_price
                ref_price.append(price)

                if result == 1 and hold[cnt] == 0 :
                    if (balance_portion - balance_on_krw) > min_krw and krw > min_krw:
                        upbit.buy_market_order(crypto_krw[cnt], min(balance_portion - balance_on_krw, krw) * 0.9995)
                        hold[cnt] = 1
                        print("{0:2d}:{1}_{2}\t BUY - IN REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}".format(cnt, crypto_krw[cnt], hold[cnt], ref_price[cnt], cur_price, get_percent(ref_price[cnt], cur_price), now.hour, now.minute, now.second))
                    else:
                        print("{0:2d}:{1}".format(cnt, crypto_krw[cnt]))
                else:
                    print("{0:2d}".format(cnt))    
                time.sleep(0.1)

            idx = -1
        else:
            cur_price = get_current_price(crypto_krw[idx])
            price, result = get_price_condition_curr(crypto_krw[idx])  #get ms5 ref
            # if total_balance > trading_limit_price:
            #     krw_sub = krw / 10
            #     sub_balance = cur_balance / 10
            # else:
            #     krw_sub = krw
            #     sub_balance = cur_balance

            if result == 1:
                print("{0:2d}:{1}_{2}\t Cur State REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}  <==  check in condition".format(idx, crypto_krw[idx], hold[idx], price, cur_price, get_percent(price, cur_price), now.hour, now.minute, now.second))
            elif result == 2:
                print("{0:2d}:{1}_{2}\t Cur State REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}  <==  check out condition".format(idx, crypto_krw[idx], hold[idx], price, cur_price, get_percent(price, cur_price), now.hour, now.minute, now.second))
            else:
                print("{0:2d}:{1}_{2}\t Cur State REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}".format(idx, crypto_krw[idx], hold[idx], price, cur_price, get_percent(price, cur_price), now.hour, now.minute, now.second))
            print("\n")
            
        idx += 1
        if idx >= crypto_cnt:
            idx = 0

        time.sleep(0.5)

    except Exception as e:
        print(e)
        time.sleep(1)
