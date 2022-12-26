import threading
import time
from clients import Client


class TradingAgent(threading.Thread):
    def __init__(self, client: Client, symbol: str, s2_volume, mul_buy: float, mul_sell: float):
        super().__init__()
        self.client: Client = client  # general api function
        self.s2_volume = s2_volume  # avalibale trading volume in base coin
        self.symbol = symbol  # ticker example BTCUSDT
        self.mul_buy = mul_buy
        self.mul_sell = mul_sell
        self.stop_event = threading.Event()  # event for stoping Thread
        self.name = symbol

    def __repr__(self):
        return f'{self.__class__.__name__}'

    def profit_condition(self, ask_price, bid_price):
        return ask_price*self.mul_sell/(bid_price*self.mul_buy) < 1.01

    def run(self):
        while True:

            if self.stop_event.is_set():
                self.client.cancel_open_orders(self.symbol)
                break

            time.sleep(5)
            stack = self.client.book_ticker(self.symbol)
            open_orders = self.client.open_orders(self.symbol)
            ex_info = self.client.get_symbol_info(self.symbol)
            balance_s1 = self.client.get_balance(ex_info['s1'])
            balance_s2 = self.client.get_balance(ex_info['s2'])


            if not open_orders:
                if balance_s1 and balance_s1.get('free', 0) > ex_info['min_volume']*stack['bidPrice']\
                    and self.profit_condition(stack['askPrice'], stack['bidPrice']):

                    price = round(stack['askPrice']*self.mul_sell, ex_info['price_precision'])
                    quantity = round(balance_s1.get('free', 0), ex_info['volume_precision'])

                    self.client.create_order(self.symbol, 'SELL', price, quantity)
                else:
                    price = round(stack['bidPrice']*self.mul_buy,ex_info['price_precision'])
                    quantity = round(self.s2_volume/price, ex_info['volume_precision'])

                    self.client.create_order(self.symbol, 'BUY', price, quantity)
            else:
                if open_orders['side'] == 'BUY'\
                    and open_orders['price'] < stack['bidPrice']:

                    self.client.cancel_open_orders(self.symbol)

                    if self.profit_condition(stack['askPrice'], stack['bidPrice']):
                        price = round(stack['bidPrice']*self.mul_buy,ex_info['price_precision'])
                        quantity = round(self.s2_volume/price, ex_info['volume_precision'])

                        self.client.create_order(self.symbol, 'BUY', price, quantity)

                elif open_orders['side'] == 'SELL'\
                    and open_orders['price'] > stack['askPrice']:

                    self.client.cancel_open_orders(self.symbol)
                    price = round(stack['askPrice']*self.mul_sell, ex_info['price_precision'])
                    quantity = round(balance_s1.get('free', 0),ex_info['volume_precision'])

                    self.client.create_order(self.symbol, 'SELL', price, quantity)

            
