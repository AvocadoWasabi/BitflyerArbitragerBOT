import logging
from datetime import datetime, timedelta
from time import sleep

from config import Config
from asset_list import AssetList

logger = logging.getLogger(__name__)

class Scheduler(object):
    def __init__(self, config, market_list):
        self.config = config
        self.market_list = market_list
        self.latest_board_checking = None
        self.on_maturity = {}
        self.on_itayose = {}

    def check_reboot_time(self):
        now = datetime.now()
        reboot_datetimes = self.market_list.get_reboot_datetimes()
        flg = False

        if self.config.config_data['maturity_debug_mode']: #Debug-mode
            for futures_type in reboot_datetimes.keys():
                start_time = datetime.strptime(self.config.config_data['debug_reboot_time'], '%Y/%m/%d %H:%M:%S')
                if start_time <= now:
                    flg = True
        else:
            for futures_type, reboot_datetime in reboot_datetimes.items():
                start_time = reboot_datetime
                if start_time <= now:
                    flg = True
        return flg

    def check_itayose_time(self):
        now = datetime.now()
        itayose_datetimes = self.market_list.get_itayose_datetimes()
        sq_settlement_datetimes = self.market_list.get_sq_settlement_datetimes()
        flg = False

        if self.config.config_data['maturity_debug_mode']: #Debug-mode sq-settelemt is 5 minutes after debug-itayose
            for futures_type in itayose_datetimes.keys():
                itayose_start = datetime.strptime(self.config.config_data['debug_itayose_time'], '%Y/%m/%d %H:%M:%S')
                sq_settlement = datetime.strptime(self.config.config_data['debug_itayose_time'], '%Y/%m/%d %H:%M:%S') + timedelta(minutes=5)
                if itayose_start <= now and now < sq_settlement:
                    flg = True
        else: 
            for futures_type, itayose_datetime in itayose_datetimes.items():
                itayose_start = itayose_datetime
                sq_settlement = sq_settlement_datetimes[futures_type]
                if itayose_start <= now and now < sq_settlement:
                    flg = True
        return flg

    def check_maturity_time(self, margin_flg):
        now = datetime.now()
        maturity_datetimes = self.market_list.get_maturity_datetimes()
        flg = False
        self.on_maturity = {}
        if self.config.config_data['maturity_debug_mode']: #Debug-mode
            for futures_type in maturity_datetimes.keys():
                if margin_flg: 
                    caliblated_time_start = datetime.strptime(self.config.config_data['debug_maturity_start'], '%Y/%m/%d %H:%M:%S') - timedelta(seconds= self.config.config_data['maturity_time_margin'])
                else:
                    caliblated_time_start = datetime.strptime(self.config.config_data['debug_maturity_start'], '%Y/%m/%d %H:%M:%S')
                if caliblated_time_start <= now:
                    flg = True
                    self.on_maturity[futures_type] = True
                else:
                    pass
        else:
            for futures_type, maturity_datetime in maturity_datetimes.items():
                if margin_flg: 
                    caliblated_time_start = maturity_datetime - timedelta(seconds= self.config.config_data['maturity_time_margin'])
                else:
                    caliblated_time_start = maturity_datetime
                if caliblated_time_start <= now:
                    flg = True
                    self.on_maturity[futures_type] = True
                else:
                    pass
        return flg
