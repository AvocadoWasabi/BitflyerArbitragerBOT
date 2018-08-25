from multiprocessing import Queue
import json
import logging
from datetime import datetime
from time import sleep
logger = logging.getLogger(__name__)

"""
push ticker that has arvitrage oppotunity for DEBUG
"""

class DebugQueuePipe(object):
    def __init__(self, markets):
        self.queue = Queue()
        self.markets = markets
    
    def run(self):
        #no arbitrage oppotunity 
        test_api_response = {
            'spot_trading' : '{"channel": "lightning_executions_BTC_JPY", "message" : {"product_code":"BTC_JPY","timestamp":"2018-05-09T11:03:16.8381514Z","tick_id":7800607,"best_bid":1000000,"best_ask":1100000,"best_bid_size":0.1303,"best_ask_size":0.057,"total_bid_depth":2061.23513399,"total_ask_depth":2859.97205488,"ltp":1005502,"volume":14742.18903983,"volume_by_product":14742.18903983}}'
        }
        for futures_type, v in self.markets.futures.items():
            test_api_response[futures_type] = '{"channel": "lightning_executions_'+ v['product_code'] + '", "message" : {"product_code":"' + v['product_code'] + '","timestamp":"2018-05-09T11:03:16.8381514Z","tick_id":7800607,"best_bid":1000000,"best_ask":1100000,"best_bid_size":0.1303,"best_ask_size":0.057,"total_bid_depth":2061.23513399,"total_ask_depth":2859.97205488,"ltp":1005502,"volume":14742.18903983,"volume_by_product":14742.18903983}}'

        #arbitrage oppotunity 
        test_api_response_2 = {}
        for futures_type, v in self.markets.futures.items():
            test_api_response_2[futures_type] = '{"channel": "lightning_executions_' + v['product_code'] + '", "message" : {"product_code":"' + v['product_code'] + '","timestamp":"2018-05-09T11:03:16.8381514Z","tick_id":7800607,"best_bid":1200000,"best_ask":1300000,"best_bid_size":0.1303,"best_ask_size":0.057,"total_bid_depth":2061.23513399,"total_ask_depth":2859.97205488,"ltp":1005502,"volume":14742.18903983,"volume_by_product":14742.18903983}}'

        #close position oppotunity before SQ
        test_api_response_3 = {
            'spot_trading' : '{"channel": "lightning_executions_BTC_JPY", "message" : {"product_code":"BTC_JPY","timestamp":"2018-05-09T11:03:16.8381514Z","tick_id":7800607,"best_bid":1000000,"best_ask":1100000,"best_bid_size":0.1303,"best_ask_size":0.057,"total_bid_depth":2061.23513399,"total_ask_depth":2859.97205488,"ltp":1005502,"volume":14742.18903983,"volume_by_product":14742.18903983}}'
        }
        for futures_type, v in self.markets.futures.items():
            test_api_response_3[futures_type] = '{"channel": "lightning_executions_' + v['product_code'] + '", "message" : {"product_code":"' + v['product_code'] + '","timestamp":"2018-05-09T11:03:16.8381514Z","tick_id":7800607,"best_bid":900000,"best_ask":1000000,"best_bid_size":0.1303,"best_ask_size":0.057,"total_bid_depth":2061.23513399,"total_ask_depth":2859.97205488,"ltp":1005502,"volume":14742.18903983,"volume_by_product":14742.18903983}}'


        start = datetime.now()
        while True:

            #-10sec: no arbitrage oppotunity
            #10-11sec: arbitrage oppotunity
            #11-sec: close position oppotunity
            if (datetime.now() - start).total_seconds() < 10:
                for k,v in test_api_response.items():
                    self._logpipe(json.loads(v),k)
            if (datetime.now() - start).total_seconds() >= 10 and (datetime.now() - start).total_seconds() < 11:
                self._logpipe(json.loads(test_api_response['spot_trading']),'spot_trading')
                for k,v in test_api_response_2.items():
                    self._logpipe(json.loads(v),k)
            if (datetime.now() - start).total_seconds() >= 11:
                for k,v in test_api_response_3.items():
                    self._logpipe(json.loads(v),k)
            sleep(1)

    def _logpipe(self, data, name):
        logger.debug('Got JSON-RPC2.0 data[' + name + ']')
        data['channel_type'] = name
        logger.debug(json.dumps(data))
        self.queue.put(data)
        
  