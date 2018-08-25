import json
import logging
from time import sleep

import pybitflyer_rev

from config import Config
from scheduler import Scheduler
from messages import Messages

logger = logging.getLogger(__name__)

class Trade(object):
    def __init__(self, api, config, markets):
        self.api = api
        self.scheduler = Scheduler(config, markets)
        self.messages = Messages(config.config_data['message_language'])

    def _child_order(self, product_code, side, position_size):
        order_result = self.api.sendchildorder(
            product_code = product_code,
            child_order_type = 'MARKET',
            side= side,
            size= position_size,
            minute_to_expire = 43200, #default 30days
            time_in_force = 'GTC'
        )
        logger.debug(json.dumps(order_result))

        #check if order is proceeded normally
        if self.api.response_code == 200:
            #retuen child_order_acceptance_id
            return order_result
        else:
            return False

    def _show_order_info(self, product_code, position_size):
        logger.info(self.messages.show('BOARD_INFO'), product_code)
        logger.info(self.messages.show('MARKET_ORDER_POSITION'),str(position_size))

    def _check_child_order_in_list(self, product_code, child_order_acceptance_id):
        result = self.api.getexecutions(
            product_code = product_code,
            child_order_acceptance_id = child_order_acceptance_id
        )
        if len(result) !=0 and self.api.response_code == 200:
            return {'result' : True, 'response_code' : 200, 'response': result}
        else:
            logger.error(json.dumps(result))
            return {'result' : False, 'response_code' : self.api.response_code, 'response': result}

    def _opposite_trade_order(self, product_code, position_size, child_order_acceptance_id):
        logger.warning(self.messages.show('OPPOSITE_TRADE_SELL_SPOT_TRADING'))
        while True:
            self._show_order_info(product_code, position_size)
            order_result = self._child_order(product_code, 'SELL', position_size)
            if order_result == False:
                logger.error(self.messages.show('OPPOSITE_TRADE_RETRY'))
                sleep(3)
            else:
                logger.info(self.messages.show('OPPOSITE_TRADE_DONE'))
                break

    def arbitrage_trade(self, product_code_spot_trading, product_code_futures, futures_type, position_size, demo_mode, **demo_mode_kwargs):
        if demo_mode == True:
            return {
                'spot_trading' : {
                    'product_code' : product_code_spot_trading,
                    'child_order_acceptance_id' : 'test',
                    'size' : position_size
                },
                'futures' : {
                    'futures_type' : futures_type,
                    'product_code' : product_code_futures,
                    'child_order_acceptance_id' : 'test',
                    'size' : position_size
                }
            }            

        #discretionary order on Futures
        logger.info(self.messages.show('ORDER_FUTURES'))
        self._show_order_info(product_code_futures, position_size)
        order_result_futures = self._child_order(product_code_futures, 'SELL', position_size)

        #order checking
        if order_result_futures == False:
            #only try once
            logger.error(self.messages.show('CANT_ORDER_FUTEURES_STOP_PROCESS'))
            return False
        else:
            logger.info(self.messages.show('ORDER_DONE'))

        #discretionary order on Spot_trading
        logger.info(self.messages.show('ORDER_SPOT_TRADING'))
        self._show_order_info(product_code_spot_trading, position_size)
        order_result_spot_trading = self._child_order(product_code_spot_trading, 'BUY', position_size)

        #order checking
        if order_result_spot_trading == False:
            logger.error(self.messages.show('CANT_ORDER_SPOT_TRADING_TRY_FUTURES_OPPOSITE_TRADE'))
            self._opposite_trade_order(product_code_futures, position_size, order_result_futures['child_order_acceptance_id'])
            return False
        else:
            logger.info(self.messages.show('ORDER_DONE'))        

        return {
            'spot_trading' : {
                'product_code' : product_code_spot_trading,
                'child_order_acceptance_id' : order_result_spot_trading['child_order_acceptance_id'],
                'size' : position_size
            },
            'futures' : {
                'futures_type' : futures_type,
                'product_code' : product_code_futures,
                'child_order_acceptance_id' : order_result_futures['child_order_acceptance_id'],
                'size' : position_size
            }
        }

    def close_position(self, product_code_spot_trading, product_code_futures, futures_type, position_size):
        logging.info(self.messages.show('POTISITION_CLOSING'))

        #SELL discretionary order on Spot_trading
        logger.info(self.messages.show('ORDER_SPOT_TRADING'))
        while True:
            self.scheduler.check_maturity_time(margin_flg=1)
            if futures_type in self.scheduler.on_maturity.keys():
                logger.error(self.messages.show('STOP_PROCESS_ON_MATURITY'))
                break

            self._show_order_info(product_code_spot_trading, position_size)
            order_result_spot_trading = self._child_order(product_code_spot_trading, 'SELL', position_size)

            #order checking
            if order_result_spot_trading == False:
                logger.error(self.messages.show('RETRY_SPOT_TRADING_ORDER'))
                sleep(0.5)
            else:
                logger.info(self.messages.show('ORDER_DONE'))
                break

        #BUY discretionary order on Futures
        logger.info(self.messages.show('ORDER_FUTURES'))
        while True:
            self.scheduler.check_maturity_time(margin_flg=1)
            if futures_type in self.scheduler.on_maturity:
                logger.error(self.messages.show('STOP_PROCESS_ON_MATURITY'))
                break

            self._show_order_info(product_code_futures, position_size)
            order_result_futures = self._child_order(product_code_futures, 'BUY', position_size)

            #order checking
            if order_result_futures == False:
                logger.error(self.messages.show('RETRY_FUTURES_ORDER'))
                sleep(0.5)
            else:
                logger.info(self.messages.show('ORDER_DONE'))
                break

    def close_sq_position(self, product_code_spot_trading, position_size):
        logging.warning(self.messages.show('ITAYOSE_CLOSING_SPOT_TRADSING_POTISION'))

        #SELL discretionary order on Spot_trading
        logger.info(self.messages.show('ORDER_SPOT_TRADING'))
        while True:
            self._show_order_info(product_code_spot_trading, position_size)
            order_result_spot_trading = self._child_order(product_code_spot_trading, 'SELL', position_size)

            #order_checking
            if order_result_spot_trading == False:
                logger.error(self.messages.show('RETRY_SPOT_TRADING_ORDER'))
                sleep(0.5)
            else:
                logger.warning(self.messages.show('ORDER_DONE'))
                break
