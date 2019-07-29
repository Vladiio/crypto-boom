import os

from binance.client import Client


API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')


def main():
    client = Client(API_KEY, API_SECRET)

    depth = client.get_order_book(symbol='BNBBTC')

    prices = client.get_all_tickers()

    # print('BINANCE_API_KEY' in os.environ)
    order = client.create_test_order(
        side=Client.SIDE_BUY,
        symbol='BNBBTC',
        type=Client.ORDER_TYPE_MARKET,
        quantity=1
    )
    import ipdb
    ipdb.set_trace()


if __name__ == '__main__':
    main()
