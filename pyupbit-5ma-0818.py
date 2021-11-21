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
crypto_cnt = 100
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

ma15 = []
ma30 = []
ma60 = []

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


def get_slope(ticker):
    condition = 0

    df15 = pyupbit.get_ohlcv(ticker, interval="minute15", count=7)
    df30 = pyupbit.get_ohlcv(ticker, interval="minute30", count=7)
    
    ma5_15 = df15['close'].rolling(window=5).mean()
    ma5_30 = df30['close'].rolling(window=5).mean()

    ma2_30 = df30['close'].rolling(window=2).mean()
    ma2_15 = df15['close'].rolling(window=2).mean()

    if ma5_15[-2] < ma2_15[-2]: condition += 128
    if ma5_30[-2] < ma2_30[-2]: condition += 64
    if ma5_15[-3] < ma5_15[-2]: condition += 32
    if ma5_15[-2] < ma5_15[-1]: condition += 16
    if ma5_30[-3] < ma5_30[-2]: condition += 8
    if ma5_30[-2] < ma5_30[-1]: condition += 4

    
    if condition == 252:
        return 1
    else:
        return 0


def get_slope2(ticker):
    df = pyupbit.get_ohlcv(ticker, count=7)
    ma2 = df['close'].rolling(window=2).mean()
    
    if ma2[-2] < ma2[-1]:
        return 1
    else:
        return 0

    
def update_ma():
    print("=== Get ref price===")
    for idx in range(crypto_cnt):

        ticker = crypto_krw[idx];

        df15 = pyupbit.get_ohlcv(ticker, interval="minute15", count=7)
        df30 = pyupbit.get_ohlcv(ticker, interval="minute30", count=7) 
        df60 = pyupbit.get_ohlcv(ticker, interval="minute60", count=7)

        df15_ma5 = df15['close'].rolling(window=5).mean()
        df30_ma5 = df30['close'].rolling(window=5).mean()
        df60_ma5 = df60['close'].rolling(window=5).mean()

        df15_ma5_price = df15_ma5[-2]
        df30_ma5_price = df30_ma5[-2]
        df60_ma5_price = df60_ma5[-2]

        ma15.append(df15_ma5_price)
        ma30.append(df30_ma5_price)
        ma60.append(df60_ma5_price)
        print("===",idx)
        time.sleep(0.2)
        


def get_ma15(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute15", count=7)
    ma5 = df['close'].rolling(window=5).mean()
    return ma5[-2]


def update_ma15():
    ma15 = []

    for idx in range(crypto_cnt):
        price15 = get_ma15(crypto_krw[idx])
        ma15.append(price15)
        time.sleep(0.1)
    crypto_print("ma15:", ma15)
    return 0


def get_ma30(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute30", count=7)
    ma5 = df['close'].rolling(window=5).mean()
    return ma5[-2]


def update_ma30():
    ma30 = []

    for idx in range(crypto_cnt):
        price30 = get_ma30(crypto_krw[idx])
        ma30.append(price30)
        time.sleep(0.1)
    crypto_print("ma30:", ma30)
    return 0


def get_ma60(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=7)
    ma5 = df['close'].rolling(window=5).mean()
    return ma5[-2]


def update_ma60():
    ma60 = []

    for idx in range(crypto_cnt):
        price60 = get_ma60(crypto_krw[idx])
        ma60.append(price60)
        time.sleep(0.1)
    crypto_print("ma60:",ma60)
    return 0


def get_close(ticker):
    df = pyupbit.get_ohlcv(ticker, count=7)
    close2 = df['close']
    return close2[-2]


def get_ref_price(ticker):
    # """MA5 * 1%fh  매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    ma5 = df['close'].rolling(window=5).mean()
    return ma5[-2]

def get_price_condition(ticker):
    # """MA5 * 1%fh  매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    df_close = df['close']
    ma5 = df['close'].rolling(window=5).mean()
    if df_close[-3] < ma5[-2] and ma5[-2] < df_close[-2] and df_close[-2] < df_close[-3] * 1.3:
        result = 1
    elif df_close[-3] > ma5[-2] and ma5[-2] > df_close[-2]:
        result = 2
    else:
        result = 0
    return ma5[-2], result

def get_price_condition_curr(ticker):
    # """MA5 * 1%fh  매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    df_close = df['close']
    ma5 = df['close'].rolling(window=5).mean()

    #if df_close[-1] >= (df_close[-2] * 1.3):
        #result = 3
    if df_close[-2] < ma5[-1] and ma5[-1] < df_close[-1]:
        result = 1
    elif df_close[-2] > ma5[-1] and ma5[-1] > df_close[-1]:
        result = 2
    else:
        result = 0
    return ma5[-1], result


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

            ma15 = []
            ma30 = []
            ma60 = []
            hold = [0] * crypto_cnt
            max_price = [0] * crypto_cnt
            
            buy_price = 0
            count = 0


            print("== Get crypto list==")
            crypto_krw, crypto = get_ticker()           #get 100 item sorted by acc_trading price

            print("== Chk holding crypto ==")
            for cnt in range(len(crypto_krw)):  #sellout out of
                buy_price = get_buy_price(crypto[cnt])  #매수가
                balance = get_balance(crypto[cnt])
                cur_price = get_current_price(crypto_krw[cnt])
                if buy_price * balance > min_krw:
                    print("sell state", cnt)
                    if cnt < crypto_cnt:
                        hold[cnt] = 2
                    else:
                        forced_sell(crypto_krw[cnt], balance)
                    count += 1

                    if count == holding_cnt:
                        break
                else:
                    print("==",cnt)
                time.sleep(0.1)

            #update_ma()
                        

            for cnt in range(crypto_cnt):
                price, result = get_price_condition(crypto_krw[cnt])  #get ms5 ref
                
                krw = get_balance("KRW")
                total_balance = upbit.get_amount('ALL') + krw
                balance_portion = total_balance / holding_cnt
                
                cur_price = get_current_price(crypto_krw[cnt])
                cur_balance = get_balance(crypto[cnt])
                balance_on_krw = cur_balance * cur_price
                ref_price.append(price)

                if (hold[cnt] == 1 or hold[cnt] == 2) and (result == 2 or cur_price < ref_price[cnt]):
                    if cur_balance > (min_krw / cur_price):
                        upbit.sell_market_order(crypto_krw[cnt], cur_balance)
                        hold[cnt] = 0
                        print("{0:2d}:{1}_{2}\t SELL OUT REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}".format(cnt, crypto_krw[cnt], hold[cnt], ref_price[cnt], cur_price, get_percent(ref_price[cnt], cur_price), now.hour, now.minute, now.second))
                else:
                    print("{0:2d}".format(cnt))
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

                if get_slope(crypto_krw[cnt]) == 1 and result == 1 and hold[cnt] == 0 :
                #if get_slope(crypto_krw[cnt]) == 1 and result == 1 and ma15[cnt] < cur_price and ma30[cnt] < cur_price and ma60[cnt] < cur_price and hold[cnt] == 0 :
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
            elif result == 3 and (hold[idx] == 1 or hold[idx] == 2):
                if max_price[idx] < cur_price:
                    max_price[idx] = cur_price
                elif cur_price <= max_price[idx] * 0.95:
                    cur_balance = get_balance(crypto[idx])
                    upbit.sell_market_order(crypto_krw[idx], cur_balance)
                    max_price[idx] = 0
                    hold[idx] == 0
                
                print("{0:2d}:{1}_{2}\t Cur State REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}  <==  sudden rise".format(idx, crypto_krw[idx], hold[idx], price, cur_price, get_percent(price, cur_price), now.hour, now.minute, now.second))
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
