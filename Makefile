ETHUSDT:
	docker run -it --name ETHUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol ETHUSDT --interval 6h,4h,15m,5m --above_multiple 2

DOTUSDT:
	docker run -it --name DOTUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol DOTUSDT --interval 30m,15m,5m

BTCUSDT:
	docker run -it --name BTCUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol BTCUSDT --interval 30m,15m --above_multiple 2

BNBUSDT:
	docker run -it --name BNBUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol BNBUSDT --interval 6h,4h,30m,15m,5m

YFIIUSDT:
	docker run -it --name YFIIUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol YFIIUSDT --interval 4h,6h,15m,5m

LINKUSDT:
	docker run -it --name LINKUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol LINKUSDT --interval 6h,15m,5m

TRXUSDT:
	docker run -it --name TRXUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol TRXUSDT --interval 15m,5m

LTCUSDT:
	docker run -it --name LTCUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol LTCUSDT --interval 30m,1h,4h,15m,5m

FILUSDT:
	docker run -it --name FILUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol FILUSDT --interval 2h,4h,6h,15m,5m
