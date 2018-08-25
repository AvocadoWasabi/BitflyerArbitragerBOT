from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)

class ArbitraggeLogger(object):
    def __init__(self, markets, logging_interval = 1):
        #logginginterval[sec]
        self.logging_interval = logging_interval
        self.latest_logging = datetime.now()
        self.markets = markets
        self.trade_pairs = None
    
    def set_ticker(self, ticker):
        self.ticker = ticker

    def set_expect_profit(self, expect_profit):
        self.expect_profit = expect_profit

    def set_trade_pairs(self, trade_pairs):
        self.trade_pairs = trade_pairs
    
    def logging(self):
        now = datetime.now()
        if (now - self.latest_logging).total_seconds() >= self.logging_interval:
            logger.info('--------------------')

            #Trade Pair
            if len(self.trade_pairs.get_trade_pairs()) != 0:
                logger.info('Pairs:')
                for pair in self.trade_pairs.trade_pairs:
                    logger.info('[' + pair['spot_trading']['product_code'] + '][' + pair['futures']['product_code'] + ']' + '[fixed:' + str(pair['fixed']) + ']' +' size:' + str(pair['spot_trading']['size']))
            #Ticker
            logger.info('price[' + self.markets.spot_trading['product_code'] + ']:' + json.dumps(self.ticker['spot_trading']))
            logger.info('price[' + self.markets.futures['weekly']['product_code'] + ']:' + json.dumps(self.ticker['weekly']))
            logger.info('price[' + self.markets.futures['biweekly']['product_code'] + ']:' + json.dumps(self.ticker['biweekly']))
            logger.info('price[' + self.markets.futures['3month']['product_code'] + ']:' + json.dumps(self.ticker['3month']))
            for k,v in self.expect_profit.items():
                logger.info('expect profit[' + self.markets.futures[k]['product_code'] + ']:' + str(json.dumps(v)))
                
            self.latest_logging = datetime.now()
