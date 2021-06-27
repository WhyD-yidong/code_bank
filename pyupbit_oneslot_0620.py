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
crypto_cnt = 31
min_krw = 5000
Trading_start = False
state = BUY
idx = 0
index = 0
limit_balance = 100000000
buy_at_now = 1
get_price = 0

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
crypto_list = []
ref_price = []
buy_price = []
sell_price = []
crypto_sorted_list = []
trading_limit_price = 5000000000 #50억
searching_limit = crypto_cnt

def get_percent(src1, src2):
    p = (src1 - src2) / src1 * 100
    return p

def get_acc_trade_price(ticker):
    url = "https://api.upbit.com/v1/candles/days"
    querystring = {"market": ticker, "count": "1"}
    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()[0]['candle_acc_trade_price']


def get_ref_price(ticker):
    # """MA5 * 1%fh  매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, count=7)
    ma5 = df['close'].rolling(window=5).mean()
    last_ma5 = ma5[-2]
    return last_ma5


def get_open_price(ticker):
    df = pyupbit.get_ohlcv(ticker, count=1)
    open = df['open']
    last_open = open[-1]
    return last_open


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

        if Trading_start is False:

            crypto_sorted_list = []
            crypto_list = []
            ref_price = []
            buy_price = []
            sell_price = []
            acc_price = []

            for cnt in range(crypto_cnt):
                vol_price = get_acc_trade_price(crypto_krw[cnt])
                acc_price.append(vol_price)
                time.sleep(0.1)

            for cnt in range(crypto_cnt):
                crypto_list.append([crypto[cnt], crypto_krw[cnt], acc_price[cnt]])

            crypto_sorted_list = sorted(crypto_list, key=operator.itemgetter(2), reverse=True)
            #print(crypto_sorted_list)

            for cnt in range(crypto_cnt):
                price = get_ref_price(crypto_sorted_list[cnt][1])
                balance = get_balance(crypto_sorted_list[cnt][0])
                get_price = get_buy_price(crypto_sorted_list[cnt][0])

                if price * balance > min_krw:
                    state = SELL
                    index = cnt
                    print("we have", crypto_sorted_list[cnt][1], balance)
                    if price < get_price:
                        price = get_price

                ref_price.append(price)
                buy_price.append(price)
                sell_price.append(price)
                time.sleep(0.1)

            for cnt in range(crypto_cnt):
                if (crypto_sorted_list[cnt][2] < trading_limit_price):
                    searching_limit = cnt
                    break

            buy_at_now = 0
            Trading_start = True

        else:
            krw = get_balance("KRW")
            total_balance = upbit.get_amount('ALL') + krw

            if state is BUY:

                cur_price = get_current_price(crypto_sorted_list[idx][1])
                cur_balance = get_balance(crypto_sorted_list[idx][0])

                if total_balance > limit_balance:
                    krw_sub = krw / 10
                else:
                    krw_sub = krw

                if buy_price[idx] < cur_price:
                    if krw > min_krw:
                        upbit.buy_market_order(crypto_sorted_list[idx][1], krw_sub * 0.9995)

                        crypto_print(crypto_sorted_list[idx][1], buy_price[idx], cur_price, idx, "Buy in", now.hour, now.minute,
                                     now.second)
                        if get_balance("KRW") < min_krw:
                            state = SELL
                            buy_at_now = 1
                            index = idx
                            buy_price[idx] = cur_price
                            sell_price[idx] = buy_price[idx] * (1 - ratio)
                            get_price = cur_price
                        else:
                            idx -= 1

                    else:
                        crypto_print(crypto_sorted_list[idx][1],idx, "T_P:", buy_price[idx], "C_P", cur_price, krw, idx,
                                     "satisfy price, no resource", now.hour, now.minute, now.second)
                else:
                    crypto_print(crypto_sorted_list[idx][1],idx, "T_P:", buy_price[idx], "C_P:", cur_price, "Ready to BUY", format(get_percent(buy_price[idx],cur_price), ".2f"),  now.hour, now.minute, now.second)
                    # please update go to current price under target price during buy.#

                idx += 1

                if idx >= searching_limit:
                    idx = 0

            elif state is SELL:

                cur_price = get_current_price(crypto_sorted_list[index][1])
                cur_balance = get_balance(crypto_sorted_list[index][0])

                if total_balance > limit_balance:
                    sub_balance = cur_balance / 10
                else:
                    sub_balance = cur_balance

                if sell_price[index] > cur_price:
                    upbit.sell_market_order(crypto_sorted_list[index][1], sub_balance)
                    if get_balance(crypto_sorted_list[index][0]) < (min_krw / cur_price):
                        state = BUY
                        idx = 0
                        if buy_at_now == 1:
                            buy_price[index] = buy_price[index] * (1 + ratio)
                        crypto_print(crypto_sorted_list[index][1], sell_price[index], cur_price, index, "Sell out",
                                 now.hour, now.minute,
                                 now.second)
                else:
                    crypto_print(crypto_sorted_list[index][1], index, "T_P:", sell_price[index], "C_P:", cur_price, "Ready to SELL", format(get_percent(sell_price[index], cur_price), ".2f"),  now.hour, now.minute, now.second)
                    # please update go to current price over target price during sell.#

        if now.minute == 00 and now.second >= 00 and now.second <= 19:
            sell_price[index] = ref_price[index]

        if now.hour == 9 and now.minute == 00 and now.second >= 00 and now.second <= 19:
            Trading_start = False
            idx = 0
            index = 0

        crypto_print("===================================================")
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)