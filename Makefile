ETHUSDT:
	docker run -it --name ETHUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol ETHUSDT --interval 4h,6h,8h,12h,1d,3d,1w --above_multiple 2

DOTUSDT:
	docker run -it --name DOTUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol DOTUSDT --interval

BTCUSDT:
	docker run -it --name BTCUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol BTCUSDT --interval 4h,6h,8h,12h,1d,3d,1w --above_multiple 2

YFIIUSDT:
	docker run -it --name YFIIUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol YFIIUSDT --interval 6h,4h --above_multiple 2

LINKUSDT:
	docker run -it --name LINKUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol LINKUSDT --interval 1d,3d

TRXUSDT:
	docker run -it --name TRXUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol TRXUSDT --interval

BNBUSDT:
	docker run -it --name BNBUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol BNBUSDT --interval 2h,8h,1d,3d,1w

XRPUSDT:
	docker run -it --name XRPUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol XRPUSDT --interval

LTCUSDT:
	docker run -it --name LTCUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol LTCUSDT --interval

FILUSDT:
	docker run -it --name FILUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol FILUSDT --interval 4h,6h
