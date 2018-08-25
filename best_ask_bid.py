import sys
from multiprocessing import Process, Queue
import json
import logging
from time import sleep

from config import Config
from realtime_api import RealtimeAPI
from market_list import Marketlist
from queue_pipe import QueuePipe

import pybitflyer_rev

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class BestAskBidAdapter(object):
    def __init__(self, queue, *keys):
        self.info = {}
        self.queue = queue
        for key in keys:
            self.info[key] = {
                'best_ask' : -1,
                'best_ask_size' : -1,
                'best_bid' : -1,
                'best_bid_size' : -1
            }

    def _parse(self, raw_data):
        return {
            'best_ask' : raw_data['message']['best_ask'],
            'best_ask_size' : raw_data['message']['best_ask_size'],
            'best_bid' : raw_data['message']['best_bid'],
            'best_bid_size' : raw_data['message']['best_bid_size']
        }

    def is_firstly_all_updated(self):
        flg = True
        for dicts in self.info.values():
            for value in dicts.values():
                if value == -1:
                    flg = False
        return flg
    

    def update_ticker(self):
        #flush queue and update ticker
        while self.queue.empty() != True:
            data = self.queue.get()
            ask_bid_info = self._parse(data)
            market_type = data['channel_type']
            self.info[market_type] = ask_bid_info
            logger.debug(market_type + ':' + json.dumps(ask_bid_info))