from multiprocessing import Queue
import json
import logging
from time import sleep
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class QueuePipe(object):
    def __init__(self, markets, api, queues):
        self.queue = Queue()
        self.queues = queues
        self.api = api
        self.markets = markets
    
    def run(self):
        #First call Bitflyer Public API(Second Realtime API Queue)
        self._api_logpipe(self.api.ticker(product_code=self.markets.spot_trading['product_code'], count=1), 'spot_trading')
        self._api_logpipe(self.api.ticker(product_code=self.markets.futures['weekly']['product_code'], count=1), 'weekly')
        self._api_logpipe(self.api.ticker(product_code=self.markets.futures['biweekly']['product_code'], count=1), 'biweekly')
        self._api_logpipe(self.api.ticker(product_code=self.markets.futures['3month']['product_code'], count=1), '3month')

        while True:
            #Blundle each queue data to one queue
            self._logpipe(self.queues['spot_trading'],'spot_trading')
            self._logpipe(self.queues['weekly'],'weekly')
            self._logpipe(self.queues['biweekly'],'biweekly')
            self._logpipe(self.queues['3month'],'3month')
            sleep(0.001)
    
    def _api_logpipe(self, data, name):
        logger.debug('Got API data[' + name + ']')
        #add product_code to queue date
        data = {'channel_type' : name, 'message': data}
        logger.debug(json.dumps(data))
        self.queue.put(data)
    
    def _logpipe(self, queue, name):
        if queue.empty() != True:
            logger.debug('Got JSON-RPC2.0 data[' + name + ']')
            data = queue.get()
            data['channel_type'] = name
            logger.debug(json.dumps(data))
            self.queue.put(data)
        
  