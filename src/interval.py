from datetime import datetime, timedelta
from time import sleep
import logging

logger = logging.getLogger(__name__)

class Interval(object):
    def __init__(self):
        self.time_data = {}

    def set_interval(self, type):
        self.time_data[type] = datetime.now()

    def is_set(self, type):
        if type in self.time_data:
            return True
        else:
            return False

    def is_passed(self, type, interval):
        now = datetime.now()
        if self.time_data[type] <= now and now < self.time_data[type] + timedelta(seconds= interval):
            return False
        else:
            return True

    def remove(self, type):
        del self.time_data[type]
