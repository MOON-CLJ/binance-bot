ETHUSDT:
	docker run -it --name ETHUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol ETHUSDT --interval 3d,1w,12h,8h,15m --above_multiple 2

DOTUSDT:
	docker run -it --name DOTUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol DOTUSDT --interval 6h,4h

BTCUSDT:
	docker run -it --name BTCUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol BTCUSDT --interval 3d,1w,1d --above_multiple 2

YFIIUSDT:
	docker run -it --name YFIIUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol YFIIUSDT --interval 6h,4h --above_multiple 2

LINKUSDT:
	docker run -it --name LINKUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol LINKUSDT --interval 3d,6h,8h,1d,15m

TRXUSDT:
	docker run -it --name TRXUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol TRXUSDT --interval

BNBUSDT:
	docker run -it --name BNBUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol BNBUSDT --interval 3d,1w,6h,8h

XRPUSDT:
	docker run -it --name XRPUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol XRPUSDT --interval

LTCUSDT:
	docker run -it --name LTCUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol LTCUSDT --interval 1h,30m,6h

FILUSDT:
	docker run -it --name FILUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol FILUSDT --interval 4h,2h,15m
