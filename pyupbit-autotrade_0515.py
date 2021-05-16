import time
import pyupbit
import datetime

access = "uSzcamUv5xrwb2x89b8vNgQySU9dVrR0hGEfLkTM"
secret = "qwHiBK2448mmTxYxXB3pmtDfXpbnt0xqj1ckrtE4"

ratio = 0.01
total_cnt = 4
total_balance = 0
min_krw = 5000
CNT_index = 0
idx = 1
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
    #print(str)
    return 0


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        crypto_print(now.hour, now.minute, now.second)

        if Trading_start == False:
            BTC_ref_price = get_ref_price("KRW-BTC")
            BTC_dn_price = BTC_ref_price * (1 - ratio)
            print("BTC ref:", BTC_ref_price, "BTC dn:", BTC_dn_price)

            ETH_ref_price = get_ref_price("KRW-ETH")
            ETH_dn_price = ETH_ref_price * (1 - ratio)
            print("ETH ref:", ETH_ref_price, "ETH dn:", ETH_dn_price)

            XRP_ref_price = get_ref_price("KRW-XRP")
            XRP_dn_price = XRP_ref_price * (1 - ratio)
            print("XRP ref:", XRP_ref_price, "XRP dn:", XRP_dn_price)

            DOGE_ref_price = get_ref_price("KRW-DOGE")
            DOGE_dn_price = DOGE_ref_price * (1 - ratio)
            print("DOGE ref:", DOGE_ref_price, "DOGE dn:", DOGE_dn_price)

            ETC_ref_price = get_ref_price("KRW-ETC")
            ETC_dn_price = ETC_ref_price * (1 - ratio)
            print("ETC ref:", ETC_ref_price, "ETC dn:", ETC_dn_price)

            BCH_ref_price = get_ref_price("KRW-BCH")
            BCH_dn_price = BCH_ref_price * (1 - ratio)
            print("BCH ref:", BCH_ref_price, "BCH dn:", BCH_dn_price)

            XLM_ref_price = get_ref_price("KRW-XLM")
            XLM_dn_price = XLM_ref_price * (1 - ratio)
            print("XLM ref:", XLM_ref_price, "XLM dn:", XLM_dn_price)

            QTUM_ref_price = get_ref_price("KRW-QTUM")
            QTUM_dn_price = QTUM_ref_price * (1 - ratio)
            print("QTUM ref:", QTUM_ref_price, "QTUM dn:", QTUM_dn_price)

            Trading_start = True

        else:
            krw = get_balance("KRW")
            total_balance = upbit.get_amount('ALL') + krw
            balance_portion = total_balance / total_cnt
            crypto_print("TOTAL BALANCE", total_balance, "EACH PORTION", balance_portion)

            if idx == 1:
                BTC_cur_price = get_current_price("KRW-BTC")
                btc = get_balance("BTC")
                btc_krw = btc * BTC_cur_price

                if BTC_ref_price < BTC_cur_price:
                    if (balance_portion - btc_krw) > min_krw and krw > min_krw:
                        upbit.buy_market_order("KRW-BTC", min(balance_portion - btc_krw, krw) * 0.9995)
                        print("BUY BTC at", now.hour, now.minute, now.second, "BTC cur price:", BTC_cur_price)
                    else:
                        crypto_print("BTC buying _ out of condition")
                elif BTC_dn_price > BTC_cur_price:
                    if btc > (min_krw / BTC_cur_price):
                        upbit.sell_market_order("KRW-BTC", btc * 0.9995)
                        print("SELL BTC at", now.hour, now.minute, now.second)
                    else:
                        crypto_print("BTC selling _ out of condition")

            elif idx == 2:
                ETH_cur_price = get_current_price("KRW-ETH")
                eth = get_balance("ETH")
                eth_krw = eth * ETH_cur_price

                if ETH_ref_price < ETH_cur_price:
                    if (balance_portion - eth_krw) > min_krw and krw > min_krw:
                        upbit.buy_market_order("KRW-ETH", min(balance_portion - eth_krw, krw) * 0.9995)
                        print("BUY ETH at", now.hour, now.minute, now.second, "ETH cur price:", ETH_cur_price)
                    else:
                        crypto_print("ETH buying _ out of condition")
                elif ETH_dn_price > ETH_cur_price:
                    if eth > (min_krw / ETH_cur_price):
                        upbit.sell_market_order("KRW-ETH", eth * 0.9995)
                        print("SELL ETH at", now.hour, now.minute, now.second)
                    else:
                        crypto_print("ETH selling _ out of condition")

            elif idx == 3:
                XRP_cur_price = get_current_price("KRW-XRP")
                xrp = get_balance("XRP")
                xrp_krw = xrp * XRP_cur_price

                if XRP_ref_price < XRP_cur_price:
                    if (balance_portion - xrp_krw) > min_krw and krw > min_krw:
                        upbit.buy_market_order("KRW-XRP", min(balance_portion - xrp_krw, krw) * 0.9995)
                        print("BUY XRP at", now.hour, now.minute, now.second, "XRP cur price:", XRP_cur_price)
                    else:
                        crypto_print("XRP buying _ out of condition")
                elif XRP_dn_price > XRP_cur_price:
                    if xrp > (min_krw / XRP_cur_price):
                        upbit.sell_market_order("KRW-XRP", xrp * 0.9995)
                        print("SELL XRP at", now.hour, now.minute, now.second)
                    else:
                        crypto_print("XRP selling _ out of condition")

            elif idx == 4:
                DOGE_cur_price = get_current_price("KRW-DOGE")
                doge = get_balance("DOGE")
                doge_krw = doge * DOGE_cur_price

                if DOGE_ref_price < DOGE_cur_price:
                    if (balance_portion - doge_krw) > min_krw and krw > min_krw:
                        upbit.buy_market_order("KRW-DOGE", min(balance_portion - doge_krw, krw) * 0.9995)
                        print("BUY DOGE at", now.hour, now.minute, now.second, "DOGE cur price:", DOGE_cur_price)
                    else:
                        crypto_print("DOGE buying _ out of condition")
                elif DOGE_dn_price > DOGE_cur_price:
                    if doge > (min_krw / DOGE_cur_price):
                        upbit.sell_market_order("KRW-DOGE", doge * 0.9995)
                        print("SELL DOGE at", now.hour, now.minute, now.second)
                    else:
                        crypto_print("DOGE selling _ out of condition")

            elif idx == 5:
                ETC_cur_price = get_current_price("KRW-ETC")
                etc = get_balance("ETC")
                etc_krw = etc * ETC_cur_price

                if ETC_ref_price < ETC_cur_price:
                    if (balance_portion - etc_krw) > min_krw and krw > min_krw:
                        upbit.buy_market_order("KRW-ETC", min(balance_portion - etc_krw, krw) * 0.9995)
                        print("BUY ETC at", now.hour, now.minute, now.second, "ETC cur price:", ETC_cur_price)
                    else:
                        crypto_print("ETC buying _ out of condition")
                elif ETC_dn_price > ETC_cur_price:
                    if etc > (min_krw / ETC_cur_price):
                        upbit.sell_market_order("KRW-ETC", etc * 0.9995)
                        print("SELL ETC at", now.hour, now.minute, now.second)
                    else:
                        crypto_print("ETC selling _ out of condition")

            elif idx == 6:
                BCH_cur_price = get_current_price("KRW-BCH")
                bch = get_balance("BCH")
                bch_krw = bch * BCH_cur_price

                if BCH_ref_price < BCH_cur_price:
                    if (balance_portion - bch_krw) > min_krw and krw > min_krw:
                        upbit.buy_market_order("KRW-BCH", min(balance_portion - bch_krw, krw) * 0.9995)
                        print("BUY BCH at", now.hour, now.minute, now.second, "BCH cur price:", BCH_cur_price)
                    else:
                        crypto_print("BCH buying _ out of condition")
                elif BCH_dn_price > BCH_cur_price:
                    if bch > (min_krw / BCH_cur_price):
                        upbit.sell_market_order("KRW-BCH", bch * 0.9995)
                        print("SELL BCH at", now.hour, now.minute, now.second)
                    else:
                        crypto_print("BCH selling _ out of condition")

            elif idx == 7:
                XLM_cur_price = get_current_price("KRW-XLM")
                xlm = get_balance("XLM")
                xlm_krw = xlm * XLM_cur_price

                if XLM_ref_price < XLM_cur_price:
                    if (balance_portion - xlm_krw) > min_krw and krw > min_krw:
                        upbit.buy_market_order("KRW-XLM", min(balance_portion - xlm_krw, krw) * 0.9995)
                        print("BUY XLM at", now.hour, now.minute, now.second, "XLM cur price:", XLM_cur_price)
                    else:
                        crypto_print("XLM buying out of condition")
                elif XLM_dn_price > XLM_cur_price:
                    if xlm > (min_krw / XLM_cur_price):
                        upbit.sell_market_order("KRW-XLM", xlm * 0.9995)
                        print("BUY XLM at", now.hour, now.minute, now.second, "XLM cur price:", XLM_cur_price)
                    else:
                        crypto_print("XLM selling _ out of condition")

            elif idx == 8:
                QTUM_cur_price = get_current_price("KRW-QTUM")
                qtum = get_balance("QTUM")
                qtum_krw = qtum * QTUM_cur_price

                if QTUM_ref_price < QTUM_cur_price:
                    if (balance_portion - qtum_krw) > min_krw and krw > min_krw:
                        upbit.buy_market_order("KRW-QTUM", min(balance_portion - qtum_krw, krw) * 0.9995)
                        print("BUY QTUM at", now.hour, now.minute, now.second, "QTUM cur price:", QTUM_cur_price)
                    else:
                        crypto_print("QTUM buying _ out of condition")
                elif QTUM_dn_price > QTUM_cur_price:
                    if qtum > (min_krw / QTUM_cur_price):
                        upbit.sell_market_order("KRW-QTUM", qtum * 0.9995)
                        print("BUY QTUM at", now.hour, now.minute, now.second, "QTUM cur price:", QTUM_cur_price)
                    else:
                        crypto_print("QTUM selling _ out of condition")
                idx = 0

            idx += 1

        crypto_print("===========================================================================")
        now = datetime.datetime.now()

        if now.hour == 9 and now.minute == 00 and now.second >= 00 and now.second <= 7: Trading_start = False
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)