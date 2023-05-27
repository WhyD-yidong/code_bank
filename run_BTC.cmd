@echo off
setlocal enabledelayedexpansion

call C:\Users\USER\Anaconda3\Scripts\activate.bat

python main.py --mode train --ver v1 --name BTC_1 --stock_code KRW-BTC
python main.py --mode train --ver v1 --name BTC_2 --stock_code KRW-BTC --epoches 2000
python main.py --mode train --ver v1 --name BTC_3 --stock_code KRW-BTC --epoches 3000
python main.py --mode train --ver v1 --name BTC_4 --stock_code KRW-BTC --epoches 4000
python main.py --mode train --ver v1 --name BTC_5 --stock_code KRW-BTC --epoches 5000
python main.py --mode train --ver v1 --name BTC_6 --stock_code KRW-BTC --epoches 6000
python main.py --mode train --ver v1 --name BTC_7 --stock_code KRW-BTC --epoches 7000
python main.py --mode train --ver v1 --name BTC_8 --stock_code KRW-BTC --epoches 8000
python main.py --mode train --ver v1 --name BTC_9 --stock_code KRW-BTC --epoches 9000
python main.py --mode train --ver v1 --name BTC_10 --stock_code KRW-BTC --epoches 10000
python main.py --mode train --ver v1 --name BTC_11 --stock_code KRW-BTC --epoches 11000
python main.py --mode train --ver v1 --name BTC_12 --stock_code KRW-BTC --epoches 12000
python main.py --mode train --ver v1 --name BTC_13 --stock_code KRW-BTC --epoches 13000
python main.py --mode train --ver v1 --name BTC_14 --stock_code KRW-BTC --epoches 14000