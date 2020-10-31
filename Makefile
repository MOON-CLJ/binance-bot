ETHUSDT:
	docker run -it --name ETHUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol ETHUSDT --interval 15m,5m --above_multiple 2

DOTUSDT:
	docker run -it --name DOTUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol DOTUSDT --interval 15m,5m

BTCUSDT:
	docker run -it --name BTCUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol BTCUSDT --interval 15m,5m --above_multiple 2

YFIIUSDT:
	docker run -it --name YFIIUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol YFIIUSDT --interval 15m,5m

LINKUSDT:
	docker run -it --name LINKUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol LINKUSDT --interval 15m,5m

TRXUSDT:
	docker run -it --name TRXUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol TRXUSDT --interval 15m,5m

BNBUSDT:
	docker run -it --name BNBUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol BNBUSDT --interval 15m,5m

LTCUSDT:
	docker run -it --name LTCUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol LTCUSDT --interval 15m,5m

FILUSDT:
	docker run -it --name FILUSDT_v2 -v /root/binance-bot:/binance-bot --rm traderv2 \
		python binance_bot_v2.py --symbol FILUSDT --interval 15m,5m
