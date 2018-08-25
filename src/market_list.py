import re
import logging
from datetime import datetime

import pybitflyer_rev

from config import Config
logger = logging.getLogger(__name__)

class Marketlist(object):
    def __init__(self, api, config):
        self.api = api
        self.config = config
        self.spot_trading = {'product_code' : 'BTC_JPY'}
        self.fx = {'product_code' : 'FX_BTC_JPY'}
        #parse product_code and maturity date
        self._get_market_list()
        self.futures = self._get_futures_list()

    def update(self):
        self.old_futures = self.futures
        self._get_market_list()
        self.futures = self._get_futures_list()
    
    def judge_if_new_futures_added(self):
        if self.old_futures != self.futures:
            return True
        else:
            return False
    
    def get_maturity_datetimes(self):
        result = {}
        for futures_type, value in self.futures.items():
            result[futures_type] = datetime.strptime(value['maturity_date'] + ' ' + self.config.config_data['maturity_time'], '%Y/%m/%d %H:%M:%S')
        return result

    def get_reboot_datetimes(self):
        result = {}
        for futures_type, value in self.futures.items():
            result[futures_type] = datetime.strptime(value['maturity_date'] + ' ' + self.config.config_data['reboot_time'], '%Y/%m/%d %H:%M:%S')
        return result


    def get_itayose_datetimes(self):
        result = {}
        for futures_type, value in self.futures.items():
            result[futures_type] = datetime.strptime(value['maturity_date'] + ' ' + self.config.config_data['itayose_time'], '%Y/%m/%d %H:%M:%S')
        return result

    def get_sq_settlement_datetimes(self):
        result = {}
        for futures_type, value in self.futures.items():
            result[futures_type] = datetime.strptime(value['maturity_date'] + ' ' + self.config.config_data['sq_time'], '%Y/%m/%d %H:%M:%S')
        return result

    def _get_market_list(self):
        self.market_list = self.api.market()

    def _get_futures_list(self):
        futures ={}
        #parse futures BTCJPYdd***YYYY
        pattern = r'BTCJPY[0-9]{2}[A-Z]{3}[0-9]{4}'
        repatter = re.compile(pattern)
        for market in self.market_list:
            logger.debug(market['product_code'])
            matchOB = repatter.match(market['product_code'])
            if matchOB:
                #get maturity date
                maturity_date = self._parse_maturity_date(market['product_code'])

                #categorize weekly,biweekly,3month from maturity date
                futures_type = self._categorize(maturity_date)

                #add futures key
                futures[futures_type] = {
                    'product_code' : market['product_code'],
                    'maturity_date' : maturity_date
                    }
        
        return futures
                
    def _parse_maturity_date(self, product_code):
        """
        3 characters of month is temporary provisioned. If they are wrong expression, please modify them.
        """
        month_keyword = {
            'JAN' : '01',
            'FEB' : '02',
            'MAR' : '03',
            'APR' : '04',
            'MAY' : '05',
            'JUN' : '06',
            'JUL' : '07',
            'AUG' : '08',
            'SEP' : '09',
            'OCT' : '10',
            'NOV' : '11',
            'DEC' : '12'
        }

        #BTCJPYdd***YYYY to YYYY-MM-dd
        year = product_code[11:15]
        key = product_code[8:11]
        month = month_keyword[key]
        day = product_code[6:8]
        date = year + '/' + month + '/' + day
    
        return date

    def _categorize(self, maturity_date):
        now = datetime.now()
        maturity_date = datetime.strptime(maturity_date + ' ' + self.config.config_data['maturity_time'], '%Y/%m/%d %H:%M:%S')
        delta = maturity_date - now
        if delta.days <= 6:
            return 'weekly'
        elif delta.days <=13:
            return 'biweekly'
        else:
            return '3month'
