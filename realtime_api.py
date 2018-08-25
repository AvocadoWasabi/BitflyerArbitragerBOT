import json
import websocket_rev
from time import sleep
from logging import getLogger,INFO,DEBUG,StreamHandler

from messages import Messages

logger = getLogger(__name__)

#JSON-RPC2.0 over Websocket
class RealtimeAPI(object):

    def __init__(self, url, channel, queue = None, config = None):
        self.url = url
        self.channel = channel
        self.queue = queue
        self.config = config
        self.messages = Messages(self.config.config_data['message_language'])

        self.ws = websocket_rev.WebSocketApp(self.url,header=None,on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        #define websocket
        websocket_rev.enableTrace(True)
        self.is_running = True

    def run(self):
        while True:
            self.ws.run_forever()   #loop inside, keep_running=False to break
            if self.ws.is_keyboard_interrupt:
                break
            #reconnection
            if self.config is not None:
                logger.info(self.messages.show('TRY_RECONNECTION_AFTER_SEC'), str(self.config.config_data['websocket_retry_after']))
                sleep(self.config.config_data['websocket_retry_after'])
            logger.info(self.messages.show('TRYING_RECONNECTION'))
        logger.info(self.messages.show('WEBSOCKET_PROCESS_TERMINATED'))

    def stop(self):
        logger.info(self.messages.show('STOP_WEBSOCKET_CONNECTION'))

    # websocker callbacks
    # message
    def on_message(self, ws, message):
        output = json.loads(message)['params']

        if self.queue != None:
            self.queue.put(output)
        logger.debug(message)

    # error
    def on_error(self, ws, error):
        logger.error(error)

    # close websocket
    def on_close(self, ws):
        logger.info(self.messages.show('DISCONNECTED_STREAMING_SERVER'))

    # open websocket
    def on_open(self, ws):
        logger.critical(self.messages.show('CONNECTED_STREAMING_SERVER'))
        output_json = json.dumps(
            {'method' : 'subscribe',
            'params' : {'channel' : self.channel}
            }
        )
        ws.send(output_json)
