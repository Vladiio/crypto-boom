import os
import time
import collections
import uuid

from binance.client import Client
from binance.websockets import BinanceSocketManager

from utils import setup_logger


API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')

UP_DIRECTION = 'UP'
DOWN_DIRECTION = 'DOWN'
PLATEAU_DIRECTION = 'PLATEUA'


logger = setup_logger()

CurrencyState = collections.namedtuple(
    'CurrencyState', 'id price direction timestamp')

Coin = collections = collections.namedtuple(
    'Coin', 'id purchase_price timestamp'
)

db = {'states': [], 'sleep_sec': 30, 'coin': Coin(
    uuid.uuid4(), None, None), 'profit': 11000}


def main():
    client = Client(API_KEY, API_SECRET)

    bn = BinanceSocketManager(client)
    bn.start_symbol_ticker_socket('BTCUSDS', process_message)
    bn.start()


def process_message(msg):
    current_price = float(msg['c'])
    last_state = None
    try:
        last_state = db['states'][-1]
    except IndexError:
        direction = None
        return
    else:
        direction = get_direction(
            last_state.price, current_price)
    finally:
        if last_state is not None and time.time() - last_state.timestamp < db['sleep_sec']:
            return
        current_state = CurrencyState(
            uuid.uuid4(), current_price, direction, time.time())
        db['states'].append(current_state)

        logger.info(dict(last_price=last_state and last_state.price,
                         current_price=current_state.price, direction=current_state.direction))

    if direction == PLATEAU_DIRECTION:
        return

    if should_buy(db):
        logger.info('buying BTC...')
        db['coin'] = Coin(uuid.uuid4(), current_price, time.time())
        db['profit'] -= current_price
        return

    if should_sell(db):
        profit = db['coin'].purchase_price - current_price
        db['profit'] += profit
        db['coin'] = Coin(uuid.uuid4(), None, None)
        logger.info(
            f'selling BTC for {current_price}, profit - {profit}, total profit - {db["profit"]}')

    db['states'] = remove_obsolete_if_needed(db['states'])


def get_direction(last_price, current_price):
    if last_price > current_price:
        return DOWN_DIRECTION
    elif last_price < current_price:
        return UP_DIRECTION
    else:
        return PLATEAU_DIRECTION


def should_buy(db):
    states = db['states']
    coin = db['coin']
    if coin.purchase_price is not None:
        return False
    last_active_states = get_last_active_states(states)[-3:]
    return (len(last_active_states) > 2 and
            all(state.direction == UP_DIRECTION for state in last_active_states))


def should_sell(db):
    states = db['states']
    coin = db['coin']
    if coin.purchase_price is None:
        return False
    last_active_states = get_last_active_states(states)[-2:]
    return (len(last_active_states) > 1 and
            all(state.direction == DOWN_DIRECTION for state in last_active_states))


def get_last_active_states(states):
    return [state for state in states if state.direction != PLATEAU_DIRECTION]


def remove_obsolete_if_needed(states):
    if len(states) < 50:
        return states
    states_copy = states[10:]
    return states_copy


if __name__ == '__main__':
    main()
