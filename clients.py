from abc import ABC, abstractmethod

def to_float(x):
    try:
        return  float(x)
    except:
        return x

def to_float_dict(d):
    return {k: to_float(v) for k,v in d.items()}

class Client(ABC):

    @abstractmethod
    def get_symbol_info(self, symbol: str):
        """
        return dict
        example:
        {'symbol': 'BTCUSDT',
        's1': 'BTC',
        's2': 'USDT',
        'volume_precision': 6, in BTC
        'price_precision': 2, in BTC
        'min_volume': '5', USDT
        'commission': '0'}
        """

    @abstractmethod
    def get_balance(self,symbol ='USDT'):
        """
        return dict
        example: 
            {'asset': 'USDT', 'free': 14.78853274, 'locked': 0.0}
        """


    @abstractmethod
    def open_orders(self, symbol):
        """
        {
            'symbol': 'NPASUSDT',
            'orderId': '0011ba9e4ebb4e51872a9d186c99839a',
            'orderListId': -1,
            'clientOrderId': '',
            'price': '0.0208',
            'origQty': '480.77',
            'executedQty': '0',
            'cummulativeQuoteQty': '0',
            'status': 'NEW',
            'timeInForce': '',
            'type': 'LIMIT',
            'side': 'BUY',
            'stopPrice': '',
            'icebergQty': '',
            'time': 1671969144886,
            'updateTime': '',
            'isWorking': True,
            'origQuoteOrderQty': '10.000016'
        }
        """
    
    @abstractmethod
    def book_ticker(self, symbol):
        """
        {
            'symbol': 'BTCUSDT',
            'bidPrice': '16853.09',
            'bidQty': '0.002800',
            'askPrice': '16853.10',
            'askQty': '0.422000'
        }
        """
    @abstractmethod
    def create_order(self, symbol, side, price, quantity):
        """
        
        """
    @abstractmethod
    def cancel_open_orders(self, symbol):


        ""
    @abstractmethod
    def is_valid_ticker(self, symbol):
        ""
        


        
class MexcClient(Client):
    def __init__(self, raw_client) -> None:
        super().__init__()
        self.raw_client = raw_client

    def get_symbol_info(self, symbol: str):

        map = {
        'symbol':  'symbol',
        'baseAsset': 's1',
        'quoteAsset': 's2',
        'quoteAssetPrecision': 'price_precision',
        'baseAssetPrecision': 'volume_precision' ,
        'quoteAmountPrecision': 'min_volume',
        'makerCommission': 'commission'
        }
        data = self.raw_client.exchange_info(options={'symbol': symbol})['symbols'][0]
        res = to_float_dict({map[k]: v for k, v in data.items() if k in map})
        res['price_precision'] = int(res['price_precision'])
        res['volume_precision'] = int(res['volume_precision'])
        return res

    def get_balance(self,symbol ='USDT'):
        res = next((i for i in self.raw_client.account_info()['balances'] if i['asset'] == symbol), None)
        if res:
            return to_float_dict(res)

    def open_orders(self, symbol):
        order_info = self.raw_client.open_orders(symbol)
        if order_info:
            order_info = to_float_dict(order_info[0])
        return order_info

    def book_ticker(self, symbol):
           return to_float_dict(self.raw_client.book_ticker(symbol))

    def create_order(self, symbol, side, price, quantity):
        self.raw_client.new_order(symbol, side, 'LIMIT',  options={'price': price, 'quantity': quantity})

    def cancel_open_orders(self, symbol):
        self.raw_client.cancel_open_orders(symbol)

    def is_valid_ticker(self, symbol):
        return any(s for s in self.raw_client.exchange_info()['symbols'] if s['symbol']==symbol)

    