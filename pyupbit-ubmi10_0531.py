import time
import pyupbit
import datetime


access = "uSzcamUv5xrwb2x89b8vNgQySU9dVrR0hGEfLkTM"
secret = "qwHiBK2448mmTxYxXB3pmtDfXpbnt0xqj1ckrtE4"

ratio = 0.00
total_cnt = 5
total_balance = 0
min_krw = 5000
CNT_index = 0
Trading_start = False
idx = 0
crypto_cnt = 12

## 비티코인, 이더리움, 에이다, 리플, 폴카닷, 비트코인캐시, 체인링크, 라이트코인, 스텔라루멘, 이더리움클래식, 퀀텀, 도지코인
crypto = ["BTC", "ETH", "ADA", "XRP", "DOT", "BCH", "LINK", "LTC", "XLM", "ETC", "QTUM", "DOGE"]
crypto_krw = ["KRW-BTC", "KRW-ETH", "KRW-ADA", "KRW-XRP", "KRW-DOT", "KRW-BCH", "KRW-LINK", "KRW-LTC", "KRW-XLM", "KRW-ETC", "KRW-QTUM", "KRW-DOGE"]
ref_price = []
crypto_hold = []
crypto_balance = []


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


def get_current_price(ticker):
    # """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]


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
        #crypto_print(now.hour, now.minute, now.second)

        if Trading_start == False:
            ref_price = []
            crypto_hold = []
            crypto_balance = []

            for index in range(crypto_cnt):
                price = get_ref_price(crypto_krw[index])
                balance = get_balance(crypto[index])

                if price * balance > min_krw:
                    crypto_hold.append(1)
                else:
                    crypto_hold.append(0)

                ref_price.append(price)
                crypto_balance.append(balance)
                time.sleep(0.1)

            crypto_print(ref_price)
            crypto_print(crypto_balance)
            crypto_print(crypto_hold)

            Trading_start = True

        else:
            krw = get_balance("KRW")
            total_balance = upbit.get_amount('ALL') + krw
            balance_portion = total_balance / total_cnt
            #print("Total Balance:", total_balance, "Each Portion:", balance_portion)

            cur_price = get_current_price(crypto_krw[idx])
            cur_balance = get_balance(crypto[idx])
            balance_on_krw = cur_balance * cur_price

            if ref_price[idx] < cur_price:
                if (balance_portion - balance_on_krw) > min_krw and krw > min_krw:
                    upbit.buy_market_order(crypto_krw[idx], min(balance_portion - balance_on_krw, krw) * 0.9995)
	            crypto_print(crypto_krw[idx], ref_price[idx], cur_price, idx, "Buy in",now.hour, now.minute, now.second)
                else:
                    crypto_print(crypto_krw[idx], ref_price[idx], cur_price, balance_portion, krw, "buying - out of condition #1", now.hour, now.minute, now.second)
            elif ref_price[idx] > cur_price:
                if cur_balance > (min_krw / cur_price):
		    upbit.sell_market_order(crypto_krw[idx], cur_balance * 0.9995)
		    crypto_print(crypto_krw[idx], ref_price[idx], cur_price, idx, "Sell out",now.hour, now.minute, now.second)
                else:
                    crypto_print(crypto_krw[idx], ref_price[idx], cur_price, balance, min_krw / cur_price, "selling - out of condition #1", now.hour, now.minute, now.second)

            idx += 1

            if idx >= crypto_cnt:
                idx = 0

        crypto_print("===========================================================================")

        if now.hour == 9 and now.minute == 00 and now.second >= 00 and now.second <= 19: Trading_start = False
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)
