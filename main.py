import sys
import json
from time import sleep
from datetime import datetime, timedelta
from multiprocessing import Process, Queue

import pybitflyer_rev

from realtime_api import RealtimeAPI
from config import Config
from arbitrager import Arbitrager
from market_list import Marketlist
from queue_pipe import QueuePipe
from debug_queue_pipe import DebugQueuePipe
from asset_list import AssetList
from scheduler import Scheduler
from messages import Messages

import logging

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))

now = datetime.now()
now_str = now.strftime('%Y%m%d')

#handler2 for file output
handler2 = logging.FileHandler(filename= now_str + ".log")
handler2.setLevel(logging.INFO)
handler2.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))

#handler3 for only high_level log and for file output
handler3 = logging.FileHandler(filename= now_str + "_high_level.log")
handler3.setLevel(logging.WARNING)
handler3.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(message)s"))


logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(handler2)
logger.addHandler(handler3)


class MainProcess(object):
    def __init__(self):
        self.processes = []
        self.config = Config()
        self.config.read_config()
        self.messages = Messages(self.config.config_data['message_language'])
    def _start_up(self):
        #read config
        assets = AssetList()
        api_key = self.config.config_data['api_key']
        api_secret = self.config.config_data['api_secret']
        demo_mode = self.config.config_data['demo_mode']
        logger.info('DEMO-mode:' + str(demo_mode))

        #queue for multi processing
        q = {}
        for asset in assets.keys(): 
            q[asset] = Queue()

        #pybirflyer API setting
        api = pybitflyer_rev.API(api_key=api_key, api_secret=api_secret)
        # getting spot_trading, futures product_code
        self.markets = Marketlist(api, self.config)
        channel = {
            'spot_trading' : 'lightning_ticker_' + self.markets.spot_trading['product_code'],
            'fx' : 'lightning_ticker_' + self.markets.fx['product_code']
        }
        for k,v in self.markets.futures.items():
            channel[k] = 'lightning_ticker_' + v['product_code']

        self.scheduler = Scheduler(self.config, self.markets)

        #get commission rate into config
        commision_rate = {
            'spot_trading': api.commission_rate(product_code = self.markets.spot_trading['product_code'])['commission_rate'],
        }

        self.config.set_commission_rate('spot_trading', commision_rate['spot_trading'])

        #Realtime API
        url = 'wss://ws.lightstream.bitflyer.com/json-rpc'

        r_api = {}
        for asset in assets.keys():
            r_api[asset] = RealtimeAPI(url, channel[asset], q[asset], self.config)

        if self.config.config_data['arbitrage_debug_mode']:
            queue_pipe = DebugQueuePipe(markets = self.markets)
        else:
            queue_pipe = QueuePipe(markets = self.markets, api = api, queues = q)

        arbitrager = Arbitrager(config=self.config, queue=queue_pipe.queue, markets=self.markets, api=api)

        self.processes = {
            'queue_pipe' : Process(target= queue_pipe.run),
            'arbitrager' : Process(target= arbitrager.run)
            }
        for asset in assets.keys():
            self.processes[asset] = Process(target= r_api[asset].run)

        for p in self.processes.values():
            p.start()    

    def _terminate_process(self):
        sleep(1)
        for p in self.processes.values():
            p.terminate()    
    
    def _reboot(self):
        self._terminate_process()
        self._start_up()
            
    def main(self):
        self._start_up()
        flg_maturity_process = False
        last_maturity = datetime.now() - timedelta(hours=25) #last maturity time is regarded as 25hours before on Firstboot. Reboot doesn't occur unless 24hours passes after maturity time.
        while True:
            try:
                if self.scheduler.check_maturity_time(margin_flg = 1) and flg_maturity_process == False:
                    flg_maturity_process = True
                    #On futures maturity, stop process on it.
                    for futures_type in self.scheduler.on_maturity.keys():
                        self.processes[futures_type].terminate()
                        logger.critical(self.messages.show('MATURITY_TIME_STOP_PROCESS'), futures_type, self.markets.futures[futures_type]['product_code'])

                #reboot and Update board info
                if self.scheduler.check_reboot_time():
                    delta = datetime.now() - last_maturity

                    if delta >= timedelta(hours=24):
                        self._reboot()
                        logger.critical(self.messages.show('REBOOT'))
                        last_maturity = datetime.now()
                        flg_maturity_process = False
                    
                sleep(0.001)
            except KeyboardInterrupt:
                self._terminate_process()
                with open('trade_pairs.tmp', 'w', encoding='utf-8') as f:
                    #empty tmp file on KeyboardInterruption
                    #trade_pairs don't inherit on Program Stopping.
                    pass
                sys.exit()

if __name__ == '__main__':
    main_process = MainProcess()
    main_process.main()