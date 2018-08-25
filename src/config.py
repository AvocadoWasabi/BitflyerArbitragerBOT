import json
import logging

import pybitflyer_rev

logger = logging.getLogger(__name__)
class Config(object):
    def __init__(self):
        self.config_data = '{}'
        self.comission_rate = {}

    def read_config(self):
        filename = 'config.json'
        with open(filename, 'r', encoding='utf-8') as f:
            self.config_data = json.load(f)

        return self.config_data
    
    def set_commission_rate(self, asset, comission_rate):
        self.comission_rate[asset] = comission_rate

    def get_commission_rate(self, asset):
        return self.comission_rate[asset]
        
