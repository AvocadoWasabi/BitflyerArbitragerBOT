from datetime import datetime
import logging
import pybitflyer_rev

from config import Config
from market_list import Marketlist
from messages import Messages
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class SwapPoint(object):
    def __init__(self, config, markets):
        self.swap_point_rate = config.config_data['swap_point_rate']
        self.markets = markets
        self.messages = Messages(config.config_data['message_language'])
    
    def cal_net_swap_point(self, futures_type, position_yen):
        maturity_datetime = datetime.strptime(self.markets.futures[futures_type]['maturity_date'] + ' 00:00:00', '%Y/%m/%d %H:%M:%S')
        now_datetime = datetime.strptime(datetime.now().strftime('%Y/%m/%d') + ' 00:00:00', '%Y/%m/%d %H:%M:%S')
        delta = (maturity_datetime - now_datetime).days

        logger.debug(self.messages.show('CALCULATE_SWAP_POINT'))
        logger.debug('product_code : ' + self.markets.futures[futures_type]['product_code'])
        logger.debug('maturity date' + maturity_datetime.strftime('%Y/%m/%d %H:%M:%S'))
        logger.debug('now' + now_datetime.strftime('%Y/%m/%d %H:%M:%S'))
        logger.debug(self.messages.show('NUM_OF_SWAP_POINT_OCCURRENCES'))

        net_swap_point = 0
        for i in range(delta):
            buf_swap_point = position_yen * self.swap_point_rate
            net_swap_point += buf_swap_point
            position_yen -= buf_swap_point
            logger.debug('[' + str(i+1) + '/' + str(delta) + ']')
            logger.debug(self.messages.show('NET_SWAP_POINT'), str(net_swap_point))
            logger.debug(self.messages.show('ONE_SWAP_POINT'), str(buf_swap_point))
            logger.debug(self.messages.show('POSITION_YEN') + str(position_yen))
        
        return net_swap_point

    