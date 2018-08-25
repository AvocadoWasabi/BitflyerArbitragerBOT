class Messages(object):
    def __init__(self, language):
        self.language = language
        self.messages ={
            'JP' : {
                #arbitrager.py
                'DEMO_MODE_NO_REAL_TRADE' : '*DEMO-MODEのため、実際の取引は行いません*',
                'AVAILABLE_POSITION': '取引可能量:%s',
                'OVER_MAX_POSITION' : '最大取引量を超えるため、裁定取引を中止します',
                'GOING_TO_GET_MAX_POSITION' : '最大取引量許容範囲であるsize %sをポジションに取ります',
                'DO_ARBITRAGE_TRADE_ORDER' : '裁定取引の注文をします',
                'ERROR_NO_ARBITRAGE_TRADE' : '裁定取引は行われませんでした',
                'ARBITRAGE_TRADE_ORDER_DONE' : '裁定取引注文を行いました',
                'ARBITRAGE_TRADE_PAIR_MADE' : '裁定取引ペアを作成しました',
                'CLOSE_TRADE_PAIR_BELOW' : '以下の取引ペアをクローズします:',
                'POSITION_CLOSED_PAIR_DELETED' : 'クローズしました。ペアを削除します',
                'TRADE_PAIR_CLOSED' : 'ペアを削除しました',
                'CLOSING_SPOT_TRADING_SIDE' : '以下の取引ペアの現物側をクローズします:',
                'INITIAL_PRICE_OBTAINED' : '初期取引価格の取得が完了しました。',
                'ARBITRAGE_TRADE_CHANCE' : '裁定取引機会を見つけました',
                'TRADE_PAIR_BEING_MADE' : '作成予定ペア[spot_trading:%s : %s : %s] Position:%s - Expect profit:%s]',
                'TRY_ARBITAGE_TRADE' : '裁定取引を試みます',
                'ARBITRAGE_TRADE_DONE' : '裁定取引を完了しました',
                'CLOSING_MARGIN_TIME' : 'クローズ可能なサイズです。%s[sec]だけ板が安定していた場合、クローズします',
                'FIX_TRADE_PAIR' : '取引ペアを固定します:[%s]',
                'ITAYOSE_CLOSING_TRADE_PAIR' : '板寄せのため、該当ペアをクローズします:[%s:%s]',

                #main.py
                'MATURITY_TIME_STOP_PROCESS' : '満期になったため、該当Futuresのプロセスを停止しました[%s:%s]',
                'REBOOT' : 'リブートしました',

                #realtime_api.py
                'TRY_RECONNECTION_AFTER_SEC' : '%s秒後にWebsocket再接続します',
                'TRYING_RECONNECTION' : 'Websocket再接続を試行します',
                'WEBSOCKET_PROCESS_TERMINATED' : 'Web Socketのプロセスを終了しました',
                'STOP_WEBSOCKET_CONNECTION' : 'WebSocket接続を中止しました',
                'DISCONNECTED_STREAMING_SERVER' : 'streaming serverから切断しました',
                'CONNECTED_STREAMING_SERVER' : 'streaming serverに接続しました',

                #swap_point.py
                'CALCULATE_SWAP_POINT' : 'スワップポイントを計算します',
                'NUM_OF_SWAP_POINT_OCCURRENCES' : 'スワップポイントは%s回発生します',
                'NET_SWAP_POINT' : '賞味のスワップポイント:%s',
                'ONE_SWAP_POINT' : ' 1回のスワップポイント:%s',
                'POSITION_YEN' : 'ポジション:%s',

                #trade.py
                'BOARD_INFO' : '板情報:[%s]',
                'MARKET_ORDER_POSITION' : '成行注文-数量:%s',
                'OPPOSITE_TRADE_SELL_SPOT_TRADING' : '反対売買のため、現物の売り注文を出します',
                'OPPOSITE_TRADE_RETRY' : '現物の反対売買注文ができませんでした。3秒後もう一度注文します',
                'OPPOSITE_TRADE_DONE' : '反対売買の注文が完了しました',
                'ORDER_FUTURES' : 'Futuresを注文します',
                'CANT_ORDER_FUTEURES_STOP_PROCESS' : 'futuresを注文できませんでした.対になる現物の注文も中断します',
                'ORDER_DONE' : '注文しました',
                'CANT_ORDER_SPOT_TRADING_TRY_FUTURES_OPPOSITE_TRADE' : '現物を注文できませんでした。ペアにならなかったfuturesの注文を反対売買します',
                'POTISITION_CLOSING' : '現物・先物のポジションをクローズします',
                'ORDER_SPOT_TRADING' : '現物を注文します',
                'STOP_PROCESS_ON_MATURITY' : '満期のため処理を中止しました',
                'RETRY_SPOT_TRADING_ORDER' : '現物を注文できませんでした.再試行します',
                'RETRY_FUTURES_ORDER' : 'futuresを注文できませんでした.再試行します',
                'ITAYOSE_CLOSING_SPOT_TRADSING_POTISION' : '現物のポジションをクローズします(板寄せ)',
            },
            'EN' : {
                #arbitrager.py
                'DEMO_MODE_NO_REAL_TRADE' : '*DEMO-MODE* No real trade',
                'AVAILABLE_POSITION': 'available position:%s',
                'OVER_MAX_POSITION' : 'Stop arbitrage trade due to over max trade position.',
                'GOING_TO_GET_MAX_POSITION' : 'Trying to get max available position size %s.',
                'DO_ARBITRAGE_TRADE_ORDER' : 'Doing arbitrage trade order.',
                'ERROR_NO_ARBITRAGE_TRADE' : 'Arbitrage trade NOT DONE.',
                'ARBITRAGE_TRADE_ORDER_DONE' : 'Arbitrage trade order DONE.',
                'ARBITRAGE_TRADE_PAIR_MADE' : 'Arbitrage trade pair was made.',
                'CLOSE_TRADE_PAIR_BELOW' : 'Closing trade pair below:',
                'POSITION_CLOSED_PAIR_DELETED' : 'Position closed. Deleting trade pair.',
                'TRADE_PAIR_CLOSED' : 'Trade pair deleted.',
                'CLOSING_SPOT_TRADING_SIDE' : 'Closing spot trading side below:',
                'INITIAL_PRICE_OBTAINED' : 'Initial price info obtained.',
                'ARBITRAGE_TRADE_CHANCE' : 'Arbitrage trade oppotunity FOUND.',
                'TRADE_PAIR_BEING_MADE' : 'Making trade pair[spot_trading:%s : %s : %s] Position:%s - Expect profit:%s]',
                'TRY_ARBITAGE_TRADE' : 'Try arbitrage trade',
                'ARBITRAGE_TRADE_DONE' : 'Arbitrage Trade DONE.',
                'CLOSING_MARGIN_TIME' : 'Closable size. Close after %s[sec] if the closing condition is kept.',
                'FIX_TRADE_PAIR' : 'Fix trade pair:[%s]',
                'ITAYOSE_CLOSING_TRADE_PAIR' : 'Closing Pair due to Itayose:[%s:%s]',

                #main.py
                'MATURITY_TIME_STOP_PROCESS' : 'Maturity Time. Stop Process[%s:%s]',
                'REBOOT' : 'Rebooted',

                #realtime_api.py
                'TRY_RECONNECTION_AFTER_SEC' : 'Websocket try reconnection after %s sec.',
                'TRYING_RECONNECTION' : 'Websocket trying reconnection',
                'WEBSOCKET_PROCESS_TERMINATED' : 'Web Socket process terminated',
                'STOP_WEBSOCKET_CONNECTION' : 'Stop Web Socket Connection',
                'DISCONNECTED_STREAMING_SERVER' : 'disconnected streaming server',
                'CONNECTED_STREAMING_SERVER' : 'connected streaming server',

                #swap_point.py
                'CALCULATE_SWAP_POINT' : 'calculate swap point',
                'NUM_OF_SWAP_POINT_OCCURRENCES' : 'swap point occurs %s times',
                'NET_SWAP_POINT' : 'net swap point:%s',
                'ONE_SWAP_POINT' : '    swap point:%s',
                'POSITION_YEN' : 'open position:%s',

                #trade.py
                'BOARD_INFO' : 'Board info:[%s]',
                'MARKET_ORDER_POSITION' : 'market order-size:%s',
                'OPPOSITE_TRADE_SELL_SPOT_TRADING' : 'Ordering spot-trading-SELL for opposite order',
                'OPPOSITE_TRADE_RETRY' : 'Can\'t spot-trading-opposite-order. Trying after 3sec.',
                'OPPOSITE_TRADE_DONE' : 'Opposite order DONE',
                'ORDER_FUTURES' : 'Ordering Futures',
                'CANT_ORDER_FUTEURES_STOP_PROCESS' : 'Can\'t order futures. Stop ordering spot-trading',
                'ORDER_DONE' : 'Order DONE',
                'CANT_ORDER_SPOT_TRADING_TRY_FUTURES_OPPOSITE_TRADE' : 'Can\'t order spot trading. Try opposite-order of futures.',
                'POTISITION_CLOSING' : 'Position closing...',
                'ORDER_SPOT_TRADING' : 'Ordering spot trading',
                'STOP_PROCESS_ON_MATURITY' : 'Stopping process on maturity time.',
                'RETRY_SPOT_TRADING_ORDER' : 'Can\'t order spot trading. Retry.',
                'RETRY_FUTURES_ORDER' : 'Can\'t order futures trading. Retry.',
                'ITAYOSE_CLOSING_SPOT_TRADSING_POTISION' : 'Closing spot-trading-position(Itayose)',
            }
        }
    def show(self, message_type):
        return self.messages[self.language][message_type]
    

