import time
import pyupbit
import datetime
import requests
import operator

access = "uSzcamUv5xrwb2x89b8vNgQySU9dVrR0hGEfLkTM"
secret = "qwHiBK2448mmTxYxXB3pmtDfXpbnt0xqj1ckrtE4"

BUY = 0
SELL = 1
price_lim = 0.05
ratio = 0.03
crypto_cnt = 20
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
min_price = []
max_price = []
sell_price = []
get_price = []

hold = []

idx = 0

def get_percent(src1, src2):
    p = (src2 - src1) / src1 * 100
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

    print("Get Ticker")

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
    condition = 0

    df15 = pyupbit.get_ohlcv(ticker, interval="minute15", count=7)
    
    ma5_15 = df15['close'].rolling(window=5).mean()

    
    if ma5_15[-3] < ma5_15[-2] and ma5_15[-2] < ma5_15[-1]:
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
    #pass


def clear_all():
    print("clear all")
    for cnt in range(100):
        print("clear ",cnt)
        balance = get_balance(crypto[cnt])
        forced_sell(crypto_krw[cnt], balance)
    return 0
    

def update_sell_price(index, cur_price):
    get_price = get_buy_price(crypto[index])

   
    if hold[index] is not 0:
        if cur_price > get_price * 1.8:
            sell_price[idx] = max_price[idx] * 0.70
        elif cur_price > get_price * 1.4:
            sell_price[idx] = max_price[idx] * 0.85
        elif cur_price > get_price * 1.2:
            sell_price[idx] = max_price[idx] * 0.90
        elif cur_price > get_price * 1.1:
            sell_price[idx] = max_price[idx] * 0.95
        else:
            sell_price[idx] = max_price[idx] * 0.97
    else:
        sell_price[idx] = min_price[idx]

    return 0


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

        if Trading_start == False:
            min_price = []
            max_price = []
            sell_price = []
            get_price = []

            hold = [0] * crypto_cnt
            
            buy_price = 0

            
            crypto_krw, crypto = get_ticker()           #get 100 item sorted by acc_trading price
            #clear_all()
            
            for cnt in range(crypto_cnt):
                price = get_current_price(crypto_krw[cnt])  #get ms5 ref
                print(cnt, crypto_krw[cnt])

                min_price.append(price*100)
                max_price.append(price/100)
                sell_price.append(price)
                get_price.append(price)
                time.sleep(0.1)


            idx = -1
            Trading_start = True
        else:
            krw = get_balance("KRW")
            total_balance = upbit.get_amount('ALL') + krw
            balance_portion = total_balance / holding_cnt

            cur_price = get_current_price(crypto_krw[idx])
            
            if max_price[idx] < cur_price:
                max_price[idx] = cur_price
                
            if min_price[idx] > cur_price:
                min_price[idx] = cur_price
                get_price[idx] = min_price[idx] * 1.055
                
            cur_balance = get_balance(crypto[idx])
            balance_on_krw = cur_balance * cur_price

            # if total_balance > trading_limit_price:
            #     krw_sub = krw / 10
            #     sub_balance = cur_balance / 10
            # else:
            #     krw_sub = krw
            #     sub_balance = cur_balance

            if get_price[idx] < cur_price and cur_price < get_price[idx] * 1.02 and hold[idx] == 0 and get_slope(crypto_krw[idx]) == 1:
                if (balance_portion - balance_on_krw) > min_krw and krw > min_krw:
                    upbit.buy_market_order(crypto_krw[idx], min(balance_portion - balance_on_krw, krw) * 0.9995)
                    hold[idx] = 1
                    sell_price[idx] = cur_price * (1 - ratio)
                    max_price[idx] = cur_price
                    print("{0:2d}:{1}_{2}\t BUY - IN Min:{3:7.2f}\t Get:{4:7.2f}\t cur:{5:7.2f}:({6:3.2f})%\t {7}:{8}:{9}".format(idx, crypto_krw[idx], hold[idx], min_price[idx], get_price[idx], cur_price, get_percent(min_price[idx], cur_price), now.hour, now.minute, now.second))
                else:
                    print("{0:2d}:{1}_{2}\t No Reso. Min:{3:7.2f}\t Get:{4:7.2f}\t cur:{5:7.2f}:({6:3.2f})%\t {7}:{8}:{9}".format(idx, crypto_krw[idx], hold[idx], min_price[idx], get_price[idx], cur_price, get_percent(min_price[idx], cur_price), now.hour, now.minute, now.second))
            elif sell_price[idx] > cur_price:
                if cur_balance > (min_krw / cur_price):
                    upbit.sell_market_order(crypto_krw[idx], cur_balance)
                    min_price[idx] = cur_price
                    get_price[idx] = min_price[idx] * 1.055
                    hold[idx] = 0
                    print("{0:2d}:{1}_{2}\t SELL-OUT Sell:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t max:{6:7.2f}:({7:3.2f})%\t{8}:{9}:{10}".format(idx, crypto_krw[idx], hold[idx], sell_price[idx], cur_price, get_percent(min_price[idx], cur_price), max_price[idx],get_percent(min_price[idx], max_price[idx]), now.hour, now.minute, now.second))
                else:
                    print("{0:2d}:{1}_{2}\t No Bala. Sell:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t max:{6:7.2f}:({7:3.2f})%\t{8}:{9}:{10}".format(idx, crypto_krw[idx], hold[idx], sell_price[idx], cur_price, get_percent(min_price[idx], cur_price), max_price[idx],get_percent(min_price[idx], max_price[idx]), now.hour, now.minute, now.second))
            else:
                print("{0:2d}:{1}_{2}\t No Cond. Sell:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t max:{6:7.2f}:({7:3.2f})%\t{8}:{9}:{10}".format(idx, crypto_krw[idx], hold[idx], sell_price[idx], cur_price, get_percent(min_price[idx], cur_price), max_price[idx],get_percent(min_price[idx], max_price[idx]), now.hour, now.minute, now.second))
            update_sell_price(idx, cur_price)
            
        idx += 1
        if idx >= crypto_cnt:
            idx = 0

        if (now.hour == 8 or now.hour == 14 or now.hour == 20 or now.hour == 2) and now.minute == 59 and now.second == 00:
            Trading_start = False
            idx = 0

        time.sleep(0.2)

    except Exception as e:
        print(e)
        time.sleep(1)
