from time import sleep
import json
import logging
from swap_point import SwapPoint
from arbitrage_logger import ArbitraggeLogger
from trade_pairs import TradePairs
from trade import Trade
from best_ask_bid import BestAskBidAdapter
from messages import Messages
from scheduler import Scheduler
from interval import Interval

logger = logging.getLogger(__name__)

class Arbitrager(object):
    def __init__(self, config, queue, markets, api):
        self.config = config
        self.markets = markets
        self.api = api
        self.best_ask_bid = BestAskBidAdapter(queue, 'spot_trading','weekly','biweekly','3month')
        self.trade_pairs = TradePairs()
        self.trade = Trade(self.api, config, markets)
        self.scheduler = Scheduler(self.config, self.markets)
        self.messages = Messages(self.config.config_data['message_language'])

    def _cal_expect_profit(self, futures_type, open_position):
        swap_point = SwapPoint(self.config, self.markets)

        profit = open_position * self.best_ask_bid.info[futures_type]['best_bid'] - open_position * self.best_ask_bid.info['spot_trading']['best_ask'] - swap_point.cal_net_swap_point(futures_type, open_position * self.best_ask_bid.info[futures_type]['best_bid']) - 2 * open_position * self.config.get_commission_rate('spot_trading')

        return profit

    def _check_arbitrage_availablity(self):
        def cal_available_position(futures_type, open_position):
            #Get available position
            op = open_position
            bb = self.best_ask_bid.info[futures_type]['best_bid_size']
            ba = self.best_ask_bid.info['spot_trading']['best_ask_size']
            compare = (op, bb, ba)
            min_position = min(compare)
            if min_position < 0.001: #fraction less than min trade unit is regarded as 0
                min_position = 0
            return min_position

        open_position = self.config.config_data['position_value']

        futures_types_list = ['weekly', 'biweekly', '3month']
        self.expect_profit = {}
        for futures_type in futures_types_list:
            min_position = cal_available_position(futures_type, open_position)
            self.expect_profit[futures_type] = {'expect_profit': self._cal_expect_profit(futures_type, min_position), 'position': min_position}

        flg = False
        self.arbitrage_available = {}
        for futures_type,v in self.expect_profit.items():
            if v['expect_profit'] > self.config.config_data['expect_profit_thleshold'] and not self.scheduler.check_maturity_time(margin_flg = 1):
                flg = True
                self.arbitrage_available[futures_type] = {
                    'expect_profit': v['expect_profit'],
                    'position' : v['position'],

                    #For DEMO-MODE 
                    'spot_trading_best_ask' : self.best_ask_bid.info['spot_trading']['best_ask_size'],
                    'futures_best_bid' : self.best_ask_bid.info[futures_type]['best_bid_size']
                }

        return flg
    
    def _arbitrage_trade(self):
        if self.config.config_data['demo_mode']:
            #DEMO-MODE
            logger.critical(self.messages.show('DEMO_MODE_NO_REAL_TRADE'))

        for k,v in self.arbitrage_available.items():
            available_position = self.config.config_data['max_position_value'] - self.trade_pairs.get_accumulated_position_value()
            logger.warning(self.messages.show('AVAILABLE_POSITION'),str(available_position))
            if available_position < 0.001:
                logger.error(self.messages.show('OVER_MAX_POSITION'))
                break
            elif available_position < v['position']:
                logger.warning(self.messages.show('GOING_TO_GET_MAX_POSITION'), str(available_position))
                order_size = round(available_position,3) #rounding to avoid float calculation error
            else:
                order_size = round(v['position'],3)

            #Arbitrage Trade
            logger.warning(self.messages.show('DO_ARBITRAGE_TRADE_ORDER'))
            if self.config.config_data['demo_mode']:
                trade_result = self.trade.arbitrage_trade(self.markets.spot_trading['product_code'], self.markets.futures[k]['product_code'], k ,order_size, 1, demo_mode_spot_trading_price = v['spot_trading_best_ask'], demo_mode_futures_price = v['futures_best_bid'])
            else:
                trade_result = self.trade.arbitrage_trade(self.markets.spot_trading['product_code'], self.markets.futures[k]['product_code'], k ,order_size, 0)
            
            if trade_result == False: #Try once
                logger.error(self.messages.show('ERROR_NO_ARBITRAGE_TRADE'))
                continue
            else:
                logger.info(self.messages.show('ARBITRAGE_TRADE_ORDER_DONE'))

            self.trade_pairs.make_pair(
                spot_trading = trade_result['spot_trading'],
                futures = trade_result['futures'],
                
            )

            logger.warning(self.messages.show('ARBITRAGE_TRADE_PAIR_MADE'))

        sleep(self.config.config_data['arbitrage_loop_cooling_time'])

    def _check_close_oppotunity(self):
        def check_closable_position(futures_type, closing_size):
            #close position when the position is smaller than ticker size
            list_ = [self.best_ask_bid.info['spot_trading']['best_ask_size'], self.best_ask_bid.info[futures_type]['best_ask_size'], closing_size]
            min_ = min(list_)
            if min_ >= closing_size:
                return True
            else:
                return False
        def check_ticker(futures_type,closing_size):
            #close when futures price is lower than spot-trading price
            if self.best_ask_bid.info[futures_type]['best_ask'] * closing_size <= self.best_ask_bid.info['spot_trading']['best_bid'] * closing_size:
                return True
            else:
                return False

        flg = False
        closing_futures_types = {}
        for trade_pair in self.trade_pairs.get_trade_pairs():
            futures_type = trade_pair['futures']['futures_type']
            closing_size = trade_pair['spot_trading']['size']

            if  check_ticker(futures_type,closing_size) and check_closable_position(futures_type, closing_size):
                flg = True
                closing_futures_types[futures_type] = True #For unique key, not using list
        
        return (flg, closing_futures_types)
    
    def _close_position(self, closing_futures_types):
        for trade_pair in self.trade_pairs.get_trade_pairs():
            if trade_pair['fixed'] == False and trade_pair['futures']['futures_type'] in closing_futures_types: #Only checking key existance, not if value is true or not
                logger.warning(self.messages.show('CLOSE_TRADE_PAIR_BELOW'))
                logger.warning(json.dumps(trade_pair))

                if self.config.config_data['demo_mode']:
                    #DEMO-MODE
                    logger.critical(self.messages.show('DEMO_MODE_NO_REAL_TRADE'))
                else:
                    self.trade.close_position(trade_pair['spot_trading']['product_code'],trade_pair['futures']['product_code'], trade_pair['futures']['futures_type'],trade_pair['spot_trading']['size'])
                logger.warning(self.messages.show('POSITION_CLOSED_PAIR_DELETED'))
                self.trade_pairs.omit_pair(trade_pair['id'])
                logger.warning(self.messages.show('TRADE_PAIR_CLOSED'))

    def _close_sq_position(self, futures_type):
        for trade_pair in self.trade_pairs.get_trade_pairs():
            if trade_pair['fixed'] == True and trade_pair['futures']['futures_type'] == futures_type: #Only checking futures key existance, not if value is true or not
                logger.warning(self.messages.show('CLOSING_SPOT_TRADING_SIDE'))
                logger.warning(json.dumps(trade_pair))

                if self.config.config_data['demo_mode']:
                    #DEMO-MODE
                    logger.critical(self.messages.show('DEMO_MODE_NO_REAL_TRADE'))
                else:
                    self.trade.close_sq_position(trade_pair['spot_trading']['product_code'],trade_pair['spot_trading']['size'])
                logger.warning(self.messages.show('POSITION_CLOSED_PAIR_DELETED'))
                self.trade_pairs.omit_pair(trade_pair['id'])
                logger.warning(self.messages.show('TRADE_PAIR_CLOSED'))

    def run(self):
        interval = Interval()
        arbitrage_logger = ArbitraggeLogger(markets= self.markets, logging_interval=self.config.config_data['std_stream_logging_interval'])

        #Updating board info
        while self.best_ask_bid.is_firstly_all_updated() == False:
            self.best_ask_bid.update_ticker()
        logger.info(self.messages.show('INITIAL_PRICE_OBTAINED'))

        #Core
        while True:
            #update board info
            self.best_ask_bid.update_ticker()

            #id price of futures is more than that of spot_trading(including commision rate and swap point),
            #futures short, spot_trading long
            if self._check_arbitrage_availablity():
                logger.critical(self.messages.show('ARBITRAGE_TRADE_CHANCE'))
                for k,v in self.arbitrage_available.items():
                    logger.warning(self.messages.show('TRADE_PAIR_BEING_MADE'),str(self.best_ask_bid.info['spot_trading']['best_ask']), k, str(self.best_ask_bid.info[k]['best_bid']), str(v['position']), str(v['expect_profit']))
                
                if self.trade_pairs.get_accumulated_position_value() >= self.config.config_data['max_position_value']:
                    logger.error(self.messages.show('OVER_MAX_POSITION'))
                    sleep(self.config.config_data['arbitrage_loop_cooling_time'])
                else:
                    logger.critical(self.messages.show('TRY_ARBITAGE_TRADE'))
                    self._arbitrage_trade()
                    logger.critical(self.messages.show('ARBITRAGE_TRADE_DONE'))
            
            #if there's an oppotunity of ensure profit before SQ, close position and not-FIXED pair.
            flg, closing_futures_types = self._check_close_oppotunity()
            #if 'closing_margin_time' passes with closable price, close position.
            if flg and self.config.config_data['close_pair_before_sq']:
                if not interval.is_set('close'):
                    logger.warning(self.messages.show('CLOSING_MARGIN_TIME'),str(self.config.config_data['closing_margin_time']))
                    interval.set_interval('close')
                if interval.is_passed('close', self.config.config_data['closing_margin_time']):
                    self._close_position(closing_futures_types)
                    interval.remove('close')
            else:
                if interval.is_set('close'):
                    interval.remove('close')

            #If it's maturity time, fix trade_pair
            if self.scheduler.check_maturity_time(margin_flg = 1):
                for trade_pair in self.trade_pairs.get_trade_pairs():
                    futures_type = trade_pair['futures']['futures_type']
                    if trade_pair['fixed'] == False and futures_type in self.scheduler.on_maturity.keys():
                        logger.warning(self.messages.show('FIX_TRADE_PAIR'), futures_type)
                        self.trade_pairs.fix(futures_type)
            
            #closing position on itayose time
            #the board info on maturity time is deleted because of reboot. So, product code of trade pairs is used for checking itayose time.
            if self.scheduler.check_itayose_time():
                for trade_pair in self.trade_pairs.get_trade_pairs():
                    product_code = trade_pair['futures']['product_code']
                    futures_type = trade_pair['futures']['futures_type']
                    if trade_pair['fixed']:
                        #close spot_trading position
                        logger.warning(self.messages.show('ITAYOSE_CLOSING_TRADE_PAIR'), futures_type, product_code)
                        self._close_sq_position(futures_type)

            #logging
            arbitrage_logger.set_ticker(self.best_ask_bid.info)
            arbitrage_logger.set_expect_profit(self.expect_profit)
            arbitrage_logger.set_trade_pairs(self.trade_pairs)
            arbitrage_logger.logging()

            sleep(0.001)

