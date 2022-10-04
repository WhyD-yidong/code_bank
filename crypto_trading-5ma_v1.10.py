import time
import pyupbit
import datetime
import operator

access = "uSzcamUv5xrwb2x89b8vNgQySU9dVrR0hGEfLkTM"
secret = "qwHiBK2448mmTxYxXB3pmtDfXpbnt0xqj1ckrtE4"

crypto_cnt = 109
holding_cnt = 0
min_krw = 5050  #최소trading금액

max_inv_seed = 500000000 #5억원
buying_count = 100
selling_count = 10
Trading_start = True
crypto = []
crypto_krw = []
list = []
ref_price = []
hold = []
buy_price = 0
idx = 0
hold_items = 0
checkin_cnt = 0
checkout_cnt = 0

simulation = 0


def get_percent(src1, src2):
    p = (src1 - src2) / src1 * 100
    return p


def get_acc_trade_price(ticker):
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
        time.sleep(0.1)

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
    elif (df_close[-3] > ma10[-2] and ma10[-2] > df_close[-2]) or (ma10[-2] > df_close[-3] and df_close[-3] > df_close[-2]):  #rising             
        result = 2
        ref = ma10[-2]
    #elif ((df_close[-3] > ma5[-2] and ma5[-2] > df_close[-2]) or (ma5[-2] > df_close[-2] and ma5[-2] > df_close[-3])) and (ma20[-3] - ma20[-2] > 0):   #falling
    #    result = 2
    #    ref = ma5[-2]
    else:
        result = 0
        ref = ma10[-2]
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
       
    if ((df_close[-2] < ma10[-1] and ma10[-1] < df_close[-1]) or (df_close[-2] < ma10[-1] and ma10[-1] < df_close[-1])) and (df_close[-1] < df_close[-2] * 1.3):
        result = 1
        ref = ma10[-1]
    elif (df_close[-2] >= ma10[-1] and ma10[-1] >= df_close[-1]) or (ma10[-1] >= df_close[-2] and df_close[-2] >= df_close[-1] and ma10[-2] < df_close[-2]):
        result = 2
        ref = ma10[-1]
    #elif (df_close[-2] > ma5[-1] and ma5[-1] > df_close[-1]) and (ma20[-2] - ma20[-1] > 0):
    #    result = 2
    #    ref = ma5[-1]
    else:
        result = 0
        ref = ma10[-1]
    return ref, result


def get_balance(ticker):
    if simulation == 0:
        # """잔고 조회"""
        balances = upbit.get_balances()
        for b in balances:
            if b['currency'] == ticker:
                if b['balance'] is not None:
                    return float(b['balance'])
        return 0.0
    else:
        # """잔고 조회"""
        if ticker == "KRW":
            return 6000000
        else:
            balances = upbit.get_balances()
            for b in balances:
                if b['currency'] == ticker:
                    if b['balance'] is not None:
                        return 80
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


def sell_market_order(cnt, balance):
    upbit.sell_market_order(crypto_krw[cnt], balance)
    #pass


def buy_market_order(cnt, price):
    upbit.buy_market_order(crypto_krw[cnt], price * 0.9995)
    #pass


def crypto_print(*str):
    print(str)
    # return 0


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:

        now = datetime.datetime.now()

        if now.hour == 9 and now.minute == 00 and (now.second >= 00 and now.second <= 30):
            Trading_start = True
            idx = 0
            hold_items = 0

        if Trading_start == True:
            Trading_start = False
            ref_price = []
            All_result = []
            buy_price = 0

            print("== Get crypto list==")
            crypto_krw, crypto = get_ticker()  # get all item sorted by acc_trading price
            crypto_cnt = len(crypto_krw)
            hold = [0000] * crypto_cnt  # 1000:none, 1000~2000:buying, 2000:hold, 2000~3000:selling
            unit_balance = [0] * crypto_cnt

            print("== Check SELLOUT list==")
            krw = get_balance("KRW")  # cash
            
            for cnt in range(crypto_cnt):  #sellout items
                price, result = get_price_condition(crypto_krw[cnt])  # get ms5 or ma10 ref
                ref_price.append(price)
                All_result.append(result)
                cur_balance = get_balance(crypto[cnt])                  #total count of items

                if cur_balance > 0 and result == 2:                     #sell condition
                    cur_price = get_current_price(crypto_krw[cnt])
                    balance_on_krw = cur_balance * cur_price            #total price
                    unit_balance[cnt] = cur_balance / selling_count     #unit price for each trading
                    krw += balance_on_krw

                    if (unit_balance[cnt] * cur_price > min_krw):
                        sell_market_order(cnt, unit_balance[cnt])       #<<<<<====================================
                        hold[cnt] = 2001
                        print("{0:3d}:{1}_{2:5d}\t STEP SELL REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}".format(
                            cnt, crypto_krw[cnt], hold[cnt], ref_price[cnt], cur_price,
                            get_percent(ref_price[cnt], cur_price), now.hour, now.minute, now.second))
                    elif balance_on_krw > min_krw:
                        sell_market_order(cnt, cur_balance)             #<<<<<====================================
                        hold[cnt] = 1000
                        print("{0:3d}:{1}_{2:5d}\t ONCE SELL REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}".format(
                            cnt, crypto_krw[cnt], hold[cnt], ref_price[cnt], cur_price,
                            get_percent(ref_price[cnt], cur_price), now.hour, now.minute, now.second))
                else:
                    if cur_balance > 0:
                        hold[cnt] = 10000
                        hold_items += 1
                    print("{0:3d}:{1}_{2:5d}".format(cnt, crypto_krw[cnt], hold[cnt]))
                time.sleep(0.5)

            print("== Check BUYIN list==")
            print("holding_cnt:{0} hold_items:{1} cash:{2}".format(holding_cnt, hold_items, krw))

            total_balance = upbit.get_amount('ALL') + krw
            balance_portion = total_balance /10

            if balance_portion >= max_inv_seed:
                balance_portion = max_inv_seed
                
            unit_price = balance_portion / buying_count
            print("total_balance:{0:10.2f} balance_portion:{1:9.2f} unit_price:{2:7.2f}".format(total_balance, balance_portion, unit_price))            
            for cnt in range(crypto_cnt):  #buy in items
                #price, result = get_price_condition(crypto_krw[cnt])  # get ms5 ref
                #ref_price.append(price)
                

                if hold[cnt] == 1000 and All_result[cnt] == 1 and hold_items < holding_cnt:
                    cur_price = get_current_price(crypto_krw[cnt])
                    hold_items += 1

                    if unit_price > min_krw:
                        buy_market_order(cnt, unit_price)  #<<<<<====================================
                        hold[cnt] = 1001  # to 1100
                        print("{0:3d}:{1}_{2:5d}\t STEP BUY-IN REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}".format(
                            cnt, crypto_krw[cnt], hold[cnt], ref_price[cnt], cur_price,
                            get_percent(ref_price[cnt], cur_price), now.hour, now.minute, now.second))

                    elif balance_portion > min_krw and krw > min_krw:
                        buy_market_order(cnt, balance_portion)  #<<<<<====================================
                        hold[cnt] = 2000
                        print("{0:3d}:{1}_{2:5d}\t ONCE BUY-IN REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}".format(
                            cnt, crypto_krw[cnt], hold[cnt], ref_price[cnt], cur_price,
                            get_percent(ref_price[cnt], cur_price), now.hour, now.minute, now.second))
                    else:
                        print("{0:3d}:{1}_{2:5d} Need More Credit".format(cnt, crypto_krw[cnt], hold[cnt]))
                else:
                    if hold[cnt] == 1000 and All_result[cnt] == 1:
                        print("{0:3d}:{1}_{2:5d} Need More Slot".format(cnt, crypto_krw[cnt], hold[cnt]))
                    else:
                        print("{0:3d}:{1}_{2:5d}".format(cnt, crypto_krw[cnt], hold[cnt]))
                time.sleep(0.5)

            idx = -1
        else:

            if hold[idx] == 1000 or hold[idx] == 2000:
                cur_price = get_current_price(crypto_krw[idx])
                price, result = get_price_condition_curr(crypto_krw[idx])  # get ms5 ref

                if result == 1:
                    checkin_cnt += 1
                    print(
                        "{0:3d}:{1}_{2:5d}\t Cur State REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}  <==  check in condition".format(
                            idx, crypto_krw[idx], hold[idx], price, cur_price, get_percent(price, cur_price), now.hour,
                            now.minute, now.second))
                elif result == 2:
                    checkout_cnt += 1                       
                    print(
                        "{0:3d}:{1}_{2:5d}\t Cur State REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}  <==  check out condition".format(
                            idx, crypto_krw[idx], hold[idx], price, cur_price, get_percent(price, cur_price), now.hour,
                            now.minute, now.second))
                else:
                    print("{0:3d}:{1}_{2:5d}\t Cur State REF:{3:7.2f}\t cur:{4:7.2f}:({5:3.2f})%\t {6}:{7}:{8}".format(idx,
                            crypto_krw[idx], hold[idx], price, cur_price, get_percent(price,cur_price), now.hour,
                            now.minute, now.second))
            else:
                if hold[idx] < 2000:
                    hold[idx] += 1
                    buy_market_order(idx, unit_price)  # <<<<<====================================
                    print("{0:3d}:{1}_{2:5d}\tunit:{3}\t\t\t\t\t {4}:{5}:{6}  <==  STEP BUY in".format(idx, crypto_krw[idx], hold[idx], unit_price,
                                                                                  now.hour, now.minute, now.second))
                    if hold[idx] == 1000 + buying_count:
                        hold[idx] = 2000
                elif hold[idx] < 3000:
                    hold[idx] += 1
                    sell_market_order(idx, unit_balance[idx])  # <<<<<====================================
                    print("{0:3d}:{1}_{2:5d}\tunit:{3}\t\t\t\t\t {3}:{4}:{5}  <==  STEP SELL out".format(idx, crypto_krw[idx], hold[idx],unit_balance[idx],
                                                                                  now.hour, now.minute, now.second))
                    if hold[idx] == 2000 + selling_count:
                        hold[idx] = 1000

            print("\n")

        idx += 1
        if idx >= crypto_cnt:
            idx = 0
                        
            if (checkin_cnt - checkout_cnt) >= 8:
                holding_cnt = 10
            elif (checkin_cnt - checkout_cnt) >= 6:
                holding_cnt = 9
            elif (checkin_cnt - checkout_cnt) >= 4:
                holding_cnt = 8
            elif (checkin_cnt - checkout_cnt) >= 2:
                holding_cnt = 7
            elif (checkout_cnt - checkin_cnt) >= 8:
                holding_cnt = 2
            elif (checkout_cnt - checkin_cnt) >= 6:
                holding_cnt = 3
            elif (checkout_cnt - checkin_cnt) >= 4:
                holding_cnt = 4                
            elif (checkout_cnt - checkin_cnt) >= 2:
                holding_cnt = 5                
            else:
                holding_cnt = 6
            print("===========  CHKIN:{0} CHKOUT:{1}\t HOLDING_CNT:{2} HOLD_ITEMS:{3}   =============".format(checkin_cnt, checkout_cnt, holding_cnt, hold_items))

            checkin_cnt = 0
            checkout_cnt = 0   

        time.sleep(0.5)

    except Exception as e:
        print(e)
        time.sleep(1)
