ETH:
    docker run -it --name ETHUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 python binance_bot_v2.py --symbol ETHUSDT --interval 3d,1w,12h,15m --above_multiple 2

DOT:
    docker run -it --name DOTUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 python binance_bot_v2.py --symbol DOTUSDT --interval 4h

BTC:
    docker run -it --name BTCUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 python binance_bot_v2.py --symbol BTCUSDT --interval 3d,1w,1d --above_multiple 2

YFII:
    docker run -it --name YFIIUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 python binance_bot_v2.py --symbol YFIIUSDT --interval 6h --above_multiple 2

LINK:
    docker run -it --name LINKUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 python binance_bot_v2.py --symbol LINKUSDT --interval 3d,8h,1d,15m

TRX:
    docker run -it --name TRXUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 python binance_bot_v2.py --symbol TRXUSDT --interval 12h,4h,3d

BNB:
    docker run -it --name BNBUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 python binance_bot_v2.py --symbol BNBUSDT --interval 3d,1w,8h,15m

XRP:
    docker run -it --name XRPUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 python binance_bot_v2.py --symbol XRPUSDT --interval 6h,8h,3d

LTC:
    docker run -it --name LTCUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 python binance_bot_v2.py --symbol LTCUSDT --interval 8h

FIL:
    docker run -it --name FILUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 python binance_bot_v2.py --symbol FILUSDT --interval 4h
