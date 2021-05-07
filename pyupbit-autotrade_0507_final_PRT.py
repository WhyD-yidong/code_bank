import time
import pyupbit
import datetime

access = "uSzcamUv5xrwb2x89b8vNgQySU9dVrR0hGEfLkTM"
secret = "qwHiBK2448mmTxYxXB3pmtDfXpbnt0xqj1ckrtE4"

ratio = 0.002
total_cnt = 4
total_balance = 0
min_krw = 5000
CNT_index = 0


Trading_start = False

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
            else:
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
        if Trading_start == False:
            BTC_ref_price = get_ref_price("KRW-BTC")
            BTC_up_price = BTC_ref_price * (1 + ratio)
            BTC_dn_price = BTC_ref_price * (1 - ratio)
            crypto_print("BTC ref:", BTC_ref_price, "BTC up:", BTC_up_price, "BTC dn:", BTC_dn_price)
                
            ETH_ref_price = get_ref_price("KRW-ETH")
            ETH_up_price = ETH_ref_price * (1 + ratio)
            ETH_dn_price = ETH_ref_price * (1 - ratio)
            crypto_print("ETH ref:", ETH_ref_price, "ETH up:", ETH_up_price, "ETH dn:", ETH_dn_price)
            
            XRP_ref_price = get_ref_price("KRW-XRP")
            XRP_up_price = XRP_ref_price * (1 + ratio)
            XRP_dn_price = XRP_ref_price * (1 - ratio)
            crypto_print("XRP ref:", XRP_ref_price, "XRP up:", XRP_up_price, "XRP dn:", XRP_dn_price)

            DOGE_ref_price = get_ref_price("KRW-DOGE")
            DOGE_up_price = DOGE_ref_price * (1 + ratio)
            DOGE_dn_price = DOGE_ref_price * (1 - ratio)
            crypto_print("DOGE ref:", DOGE_ref_price, "DOGE up:", DOGE_up_price, "DOGE dn:", DOGE_dn_price)

            Trading_start = True

        else:
            BTC_cur_price = get_current_price("KRW-BTC")
            btc = get_balance("BTC")
            btc_krw = btc * BTC_cur_price
            crypto_print("BTC cur price:", BTC_cur_price, "BTC balance:",btc, "BTC at KRW:", btc_krw)

            ETH_cur_price = get_current_price("KRW-ETH")
            eth = get_balance("ETH")
            eth_krw = eth * ETH_cur_price
            crypto_print("ETH cur price:", ETH_cur_price, "ETH balance:",eth, "ETH at KRW:", eth_krw)

            XRP_cur_price = get_current_price("KRW-XRP")
            xrp = get_balance("XRP")
            xrp_krw = xrp * XRP_cur_price
            crypto_print("XRP cur price:", XRP_cur_price, "XRP balance:",xrp, "XRP at KRW:", xrp_krw)

            DOGE_cur_price = get_current_price("KRW-DOGE")
            doge = get_balance("DOGE")
            doge_krw = doge * DOGE_cur_price
            crypto_print("DOGE cur price:", DOGE_cur_price, "DOGE balance:",doge, "DOGE at KRW:", doge_krw)
                
            krw = get_balance("KRW")
            total_balance = btc_krw + eth_krw + xrp_krw + doge_krw + krw
            balance_portion = total_balance / total_cnt
            crypto_print("TOTAL BALANCE", total_balance, "EACH PORTION", balance_portion)


            if BTC_up_price < BTC_cur_price:
                if (balance_portion - btc_krw) > min_krw and krw > min_krw:
                    crypto_print("within condition for BTC buying")
                    upbit.buy_market_order("KRW-BTC", min(balance_portion - btc_krw, krw) * 0.9995)
                else:
                    crypto_print("beside condition for BTC buying")
            elif BTC_dn_price > BTC_cur_price:
                if btc > (min_krw / BTC_cur_price):
                    crypto_print("within condition for BTC selling")
                    upbit.sell_market_order("KRW-BTC", btc * 0.9995)
                else:
                    crypto_print("beside condition for BTC selling")

            if ETH_up_price < ETH_cur_price:
                if (balance_portion - eth_krw) > min_krw and krw > min_krw:
                    crypto_print("within condition for ETH buying")
                    upbit.buy_market_order("KRW-ETH", min(balance_portion - eth_krw, krw) * 0.9995)
                else:
                    crypto_print("beside condition for ETH buying")
            elif ETH_dn_price > ETH_cur_price:
                if eth > (min_krw / ETH_cur_price):
                    crypto_print("within condition for ETH selling")
                    upbit.sell_market_order("KRW-ETH", eth * 0.9995)
                else:
                    crypto_print("beside condition for ETH selling")

            if XRP_up_price < XRP_cur_price:
                if (balance_portion - xrp_krw) > min_krw and krw > min_krw:
                    crypto_print("within condition for XRP buying")
                    upbit.buy_market_order("KRW-XRP", min(balance_portion - xrp_krw, krw) * 0.9995)
                else:
                    crypto_print("beside condition for XRP buying")
            elif XRP_dn_price > XRP_cur_price:
                if xrp > (min_krw / XRP_cur_price):
                    crypto_print("within condition for XRP selling")
                    upbit.sell_market_order("KRW-XRP", xrp * 0.9995)
                else:
                    crypto_print("beside condition for XRP selling")

            if DOGE_up_price < DOGE_cur_price:
                if (balance_portion - doge_krw) > min_krw and krw > min_krw:
                    crypto_print("within condition for DOGE buying")
                    upbit.buy_market_order("KRW-DOGE", min(balance_portion - doge_krw, krw) * 0.9995)
                else:
                    crypto_print("beside condition for DOGE buying")
            elif DOGE_dn_price > DOGE_cur_price:
                if doge > (min_krw / DOGE_cur_price):
                    crypto_print("within condition for DOGE selling")
                    upbit.sell_market_order("KRW-DOGE", doge * 0.9995)
                else:
                    crypto_print("beside condition for DOGE selling")

        crypto_print("===========================================================================")
        now = datetime.datetime.now()

        if now.hour == 9 and now.minute == 00 and now.second >= 00 and now.second <=7: Trading_start = False
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)
