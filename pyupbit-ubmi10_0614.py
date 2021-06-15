import time
import pyupbit
import datetime
import requests
import operator

access = "uSzcamUv5xrwb2x89b8vNgQySU9dVrR0hGEfLkTM"
secret = "qwHiBK2448mmTxYxXB3pmtDfXpbnt0xqj1ckrtE4"

ratio = 0.01
total_cnt = 2
total_balance = 0
min_krw = 5000
CNT_index = 0
Trading_start = False
idx = 0
crypto_cnt = 31

## 비트코인, 이더리움, 에이다, 도지코인, 리플, 폴카닷, 비트코인캐시, 라이트코인, 체인링크, 쎄타토큰, 스텔라루멘, 비체인,
# 이더리움클래식, 트론, 이오스, 네오, 아이오타, 쎄타퓨엘, 비트코인에스브이, 크립토닷컴체인, 코스모스, 비트토렌트, 테조스,
# 해테라해시그래프, 웨이브, 넴, 칠리즈, 질리카, 비트코인골드, 엔진코인, 퀀텀
crypto = ["BTC", "ETH", "ADA", "DOGE", "XRP", "DOT", "BCH", "LTC", "LINK", "THETA", "XLM", "VET", "ETC", "TRX", "EOS",
          "NEO", "IOTA", "TFUEL", "BSV", "CRO", "ATOM", "BTT", "XTZ", "HBAR", "WAVES", "XEM", "CHZ", "ZIL", "BTG", "ENJ", "QTUM"]
crypto_krw = ["KRW-BTC", "KRW-ETH", "KRW-ADA", "KRW-DOGE", "KRW-XRP", "KRW-DOT", "KRW-BCH", "KRW-LTC", "KRW-LINK",
              "KRW-THETA", "KRW-XLM", "KRW-VET", "KRW-ETC", "KRW-TRX", "KRW-EOS", "KRW-NEO", "KRW-IOTA", "KRW-TFUEL",
              "KRW-BSV", "KRW-CRO", "KRW-ATOM", "KRW-BTT", "KRW-XTZ", "KRW-HBAR", "KRW-WAVES", "KRW-XEM", "KRW-CHZ",
              "KRW-ZIL", "KRW-BTG", "KRW-ENJ", "KRW-QTUM"]
acc_price = []

crypto_new_list = []

ref_price = []
buy_price = []
sell_price = []
limit_price = []
crypto_hold = []
crypto_balance = []
crypto_sorted_list = []


def get_acc_trade_price(ticker):
    url = "https://api.upbit.com/v1/candles/minutes/240"
    querystring = {"market": ticker, "count": "1"}
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()[0]['candle_acc_trade_price']


def get_ref_price(ticker):
    # """MA5 * 1%fh  매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, count=7, interval="minute240")
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


def get_current_price(ticker):
    # """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


def crypto_print(*str):
    # print(str)
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
            buy_price = []
            sell_price = []
            crypto_hold = [0] * crypto_cnt
            crypto_balance = []
            acc_price = []
            crypto_new_list = []
            crypto_sorted_list = []

            for cnt in range(crypto_cnt):
                vol_price = get_acc_trade_price(crypto_krw[cnt])
                acc_price.append(vol_price)
                time.sleep(0.1)

            for irt in range(crypto_cnt):
                crypto_new_list.append([crypto[irt], crypto_krw[irt], acc_price[irt]])

            crypto_sorted_list = sorted(crypto_new_list, key=operator.itemgetter(2), reverse=True)

            for index in range(crypto_cnt):
                price = get_ref_price(crypto_sorted_list[index][1])
                balance = get_balance(crypto_sorted_list[index][0])

                ref_price.append(price)
                buy_price.append(price)
                sell_price.append(price)
                crypto_balance.append(balance)
                time.sleep(0.1)

            crypto_print(ref_price)
            crypto_print(sell_price)
            crypto_print(crypto_balance)
            crypto_print(crypto_hold)
            crypto_print(acc_price)


            Trading_start = True

        else:
            krw = get_balance("KRW")
            total_balance = upbit.get_amount('ALL') + krw
            balance_portion = total_balance / total_cnt
            # print("Total Balance:", total_balance, "Each Portion:", balance_portion)

            cur_price = get_current_price(crypto_sorted_list[idx][1])
            cur_balance = get_balance(crypto_sorted_list[idx][0])
            balance_on_krw = cur_balance * cur_price

            if buy_price[idx] < cur_price:
                if (balance_portion - balance_on_krw) > min_krw and krw > min_krw:
                    upbit.buy_market_order(crypto_sorted_list[idx][1], min(balance_portion - balance_on_krw, krw) * 0.9995)
                    crypto_hold[idx] = 1
                    buy_price[idx] = cur_price
                    sell_price[idx] = buy_price[idx] * (1 - ratio)
                    crypto_print(crypto_sorted_list[idx][1], buy_price[idx], cur_price, idx, "Buy in", now.hour, now.minute,
                                 now.second)
                else:
                    crypto_print(crypto_sorted_list[idx][1], buy_price[idx], cur_price, balance_portion, krw, idx,
                                 "buying - out of condition #1", crypto_hold[idx], now.hour, now.minute, now.second)

            elif crypto_hold[idx] == 1:
                if sell_price[idx] > cur_price:
                    if cur_balance > (min_krw / cur_price):
                        upbit.sell_market_order(crypto_sorted_list[idx][1], cur_balance * 0.9995)
                        crypto_print(crypto_sorted_list[idx][1], sell_price[idx], cur_price, idx, "Sell out", now.hour, now.minute,
                                     now.second)
                        idx = 0
                    else:
                        crypto_print(crypto_sorted_list[1][idx], sell_price[idx], cur_price, cur_balance, min_krw / cur_price, idx,
                                     "selling - out cond. this slot", crypto_hold[idx], now.hour, now.minute, now.second)

            elif sell_price[idx] > cur_price:
                if cur_balance > (min_krw / cur_price):
                    upbit.sell_market_order(crypto_sorted_list[idx][1], cur_balance * 0.9995)
                    crypto_print(crypto_sorted_list[idx][1], sell_price[idx], cur_price, idx, "Sell out", now.hour, now.minute,
                                 now.second)
                    buy_price[idx] = sell_price[idx] * (1 + ratio)
                    idx = 0
                else:
                    crypto_print(crypto_sorted_list[idx][1], sell_price[idx], cur_price, cur_balance, min_krw / cur_price, idx,
                                 "selling - out cond. other slot", crypto_hold[idx], now.hour, now.minute, now.second)
            else:
                crypto_print(crypto_sorted_list[idx][1], buy_price[idx], cur_price, sell_price[idx], "standby sell",
                             crypto_hold[idx])

            idx += 1

            if idx >= crypto_cnt:
                idx = 0

        crypto_print("===========================================================================")

        if (
                now.hour == 1 or now.hour == 5 or now.hour == 9 or now.hour == 13 or now.hour == 17 or now.hour == 21) and now.minute == 00 and now.second >= 00 and now.second <= 19: Trading_start = False
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)
