
import logging

logger = logging.getLogger(__name__)

class AssetList(object):

    def __init__(self):
        self.assets = [
            'spot_trading',
            'weekly',
            'biweekly',
            '3month'
            ]
            #fx is not used for arbitrage trade

        self.asset_futures = [
            'weekly',
            'biweekly',
            '3month'
            ]

    def keys(self):
        return self.assets
