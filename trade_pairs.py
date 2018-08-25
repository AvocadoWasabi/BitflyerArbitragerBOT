import json
import logging
logger = logging.getLogger(__name__)
class TradePairs(object):
    def __init__(self):
        self.trade_pairs = [] #ex. [ {pairs},{pairs}]
        self.pair_id = 1

        #read tmp on reboot
        with open('trade_pairs.tmp', 'r', encoding='utf-8') as f:
            try:
                self.trade_pairs = json.load(f)
            except json.JSONDecodeError:
                self.trade_pairs = []
    
    def _update_tmp_file(self):
        with open('trade_pairs.tmp', 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.trade_pairs))

    def get_trade_pairs(self):
        return self.trade_pairs
    
    def make_pair(self, spot_trading, futures):
        self.trade_pairs.append(
            
                {
                    'id' : self.pair_id,
                    'spot_trading' : {
                        'product_code' : spot_trading['product_code'],
                        'child_order_acceptance_id' : spot_trading['child_order_acceptance_id'],
                        'size' : spot_trading['size']
                    },
                    'futures' : {
                        'futures_type' : futures['futures_type'],
                        'product_code' : futures['product_code'],
                        'child_order_acceptance_id' : futures['child_order_acceptance_id'],
                        'size' : futures['size']
                    },
                    'fixed' : False #True on maturity time
                }
            )
        self.pair_id += 1
        self._update_tmp_file()
    
    def omit_pair(self, id):
        buf = []
        for i in range(len(self.trade_pairs)):
            if self.trade_pairs[i]['id'] != id:
                buf.append(self.trade_pairs[i])
        self.trade_pairs = buf
        self._update_tmp_file()

    def fix(self, futures_type):
        for i in range(len(self.trade_pairs)):
            if self.trade_pairs[i]['futures']['futures_type'] == futures_type:
                self.trade_pairs[i]['fixed'] = True

    def get_accumulated_position_value(self):
        a_position_value = 0
        for pair in self.trade_pairs:
            a_position_value += pair['spot_trading']['size']
        
        return a_position_value
