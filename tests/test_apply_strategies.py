# -*- coding: utf-8 -*-
import src.apply_strategies as strategy
import asyncio
import pytest
                      
def parse_dotenv(sub_account)->dict:    
    from src.configuration import config
    return config.main_dotenv (sub_account,
                               'test.env')                                                         
             
sub_account: str = 'deribit-147691'
client_id: str = parse_dotenv(sub_account) ['client_id']
client_secret: str = parse_dotenv(sub_account) ['client_secret']
currency: str = 'eth'

connection_url: str = 'https://www.deribit.com/api/v2/'

Strategy = strategy.ApplyHedgingSpot (None, 
                                       None,
                                       None,
                                       currency
                                            )
        
@pytest.mark.asyncio
async def test_is_send_order_allowed():
    from strategies import entries_exits
    
    open_trade =  [
        {'trade_seq': 118020115, 'trade_id': 'ETH-160804604', 'timestamp': 1677059533908, 'tick_direction': 1, 'state': 'filled', 
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1640.85, 'post_only': True, 
         'order_type': 'limit', 'order_id': 'ETH-31873685113', 'mmp': False, 'matching_id': None, 'mark_price': 1640.88, 'liquidity': 'M', 
         'label': 'test-open-1677059533', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1641.03, 'fee_currency': 'ETH', 'fee': 0.0, 
         'direction': 'sell', 'api': True, 'amount': 78.0
         }, 
        {'trade_seq': 118647438, 'trade_id': 'ETH-161557067', 'timestamp': 1677807144369, 'tick_direction': 2, 'state': 'filled',
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.00039974, 'price': 1535, 'post_only': True,
         'order_type': 'limit', 'order_id': 'ETH-31941707258', 'mmp': False, 'matching_id': None, 'mark_price': 1544.41, 'liquidity': 'M',
         'label': 'test-closed-1677059533', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1552.18, 'fee_currency': 'ETH', 'fee': 0,
         'direction': 'buy', 'api': True, 'amount': 10
         }, 
        {'trade_seq': 118697746, 'trade_id': 'ETH-161622575', 'timestamp': 1677835222867, 'tick_direction': 1, 'state': 'filled',
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0, 'price': 1569.65, 'post_only': True, 
         'order_type': 'limit', 'order_id': 'ETH-32042276354', 'mmp': False, 'matching_id': None, 'mark_price': 1569.81, 'liquidity': 'M', 
         'label': 'hedgingSpot-open-1677835222468', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1570.19, 'fee_currency': 'ETH', 'fee': 0, 
         'direction': 'sell', 'api': True, 'amount': 7}, 
        {'trade_seq': 118646176, 'trade_id': 'ETH-161555549', 'timestamp': 1677807136264, 'tick_direction': 3, 'state': 'filled', 
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0003367, 'price': 1550, 'post_only': True, 
         'order_type': 'limit', 'order_id': 'ETH-31941709815', 'mmp': False, 'matching_id': None, 'mark_price': 1555.56, 'liquidity': 'M', 
         'label': 'test-closed-1677059533', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1560.48, 'fee_currency': 'ETH', 'fee': 0,
         'direction': 'buy', 'api': True, 'amount': 10
         },
        {'trade_seq': 115425899, 'trade_id': 'ETH-157512749', 'timestamp': 1674106201607, 'tick_direction': 3, 'state': 'filled', 
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.05, 'post_only': True, 
         'order_type': 'limit', 'order_id': 'ETH-31266368853', 'mmp': False, 'matching_id': None, 'mark_price': 1528.33, 'liquidity': 'M', 
         'label': 'hedgingSpot-open-1674106085', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.78, 'fee_currency': 'ETH', 'fee': 0.0, 
         'direction': 'sell', 'api': True, 'amount': 7.0
         },
        {'trade_seq': 115426103, 'trade_id': 'ETH-157513016', 'timestamp': 1674106959423, 'tick_direction': 0, 'state': 'filled',
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1527.2, 'post_only': True,
         'order_type': 'limit', 'order_id': 'ETH-31266435353', 'mmp': False, 'matching_id': None, 'mark_price': 1526.81, 'liquidity': 'M', 
         'label': 'hedgingSpot-open-1674106880', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1526.99, 'fee_currency': 'ETH', 'fee': 0.0, 
         'direction': 'sell', 'api': True, 'amount': 7.0
         }, 
        {'trade_seq': 115426211, 'trade_id': 'ETH-157513139', 'timestamp': 1674107594720, 'tick_direction': 1, 'state': 'open', 
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 
         'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.62, 'liquidity': 'M',
         'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.52, 'fee_currency': 'ETH', 'fee': 0.0, 
         'direction': 'sell', 'api': True, 'amount': 11.0
         }, {'trade_seq': 115426212, 'trade_id': 'ETH-157513141', 'timestamp': 1674107600323, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.61, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 45.0}, {'trade_seq': 115440589, 'trade_id': 'ETH-157532557', 'timestamp': 1674134437352, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1514.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269839438', 'mmp': False, 'matching_id': None, 'mark_price': 1514.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134423', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1514.57, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 115441415, 'trade_id': 'ETH-157533765', 'timestamp': 1674134974683, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1524.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269979727', 'mmp': False, 'matching_id': None, 'mark_price': 1525.19, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134971', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1524.87, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118355869, 'trade_id': 'ETH-161212758', 'timestamp': 1677474758759, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -0.00011743, 'price': 1635.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31958514035', 'mmp': False, 'matching_id': None, 'mark_price': 1635.17, 'liquidity': 'M', 'label': 'supplyDemandLong60-open-1677473096934', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1635.36, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 9.0}, {'trade_seq': 118554841, 'trade_id': 'ETH-161447719', 'timestamp': 1677716308851, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0, 'price': 1675, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31958514019', 'mmp': False, 'matching_id': None, 'mark_price': 1675.06, 'liquidity': 'M', 'label': 'supplyDemandShort60-open-1677473096', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1674.09, 'fee_currency': 'ETH', 'fee': 0, 'direction': 'sell', 'api': True, 'amount': 8}, {'trade_seq': 118698584, 'trade_id': 'ETH-161624004', 'timestamp': 1677836968025, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0, 'price': 1566.8, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32042537117', 'mmp': False, 'matching_id': None, 'mark_price': 1566.77, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677836948224', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1566.95, 'fee_currency': 'ETH', 'fee': 0, 'direction': 'sell', 'api': True, 'amount': 10}, {'trade_seq': 118754111, 'trade_id': 'ETH-161694237', 'timestamp': 1677962858339, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 3.886e-05, 'price': 1550.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32055316625', 'mmp': False, 'matching_id': None, 'mark_price': 1550.34, 'liquidity': 'M', 'label': 'supplyDemandLong60B-open-1677903684425', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1550.76, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 5.0}
        ]

    open_orders = [
        {
            'web': False, 'triggered': False, 'trigger_price': 1720.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 
            'stop_price': 1720.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 
            'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTB-5655271', 'mmp': False, 'max_show': 9.0,
            'last_update_timestamp': 1677934800237, 'label': 'supplyDemandShort60-closed-1677934800137', 'is_liquidation': False, 
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'buy', 'creation_timestamp': 1677934800237, 'api': True, 'amount': 9.0
            }, 
        {
            'web': False, 'triggered': False, 'trigger_price': 1600.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled',
            'stop_price': 1600.0, 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1610.0, 
            'post_only': True, 'order_type': 'take_limit', 'order_state': 'untriggered', 'order_id': 'ETH-TPTS-5655237', 'mmp': False, 'max_show': 5.0,
            'last_update_timestamp': 1677903684561, 'label': 'supplyDemandLong60B-closed-1677903684425', 'is_liquidation': False, 
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'sell', 'creation_timestamp': 1677903684561, 'api': True, 'amount': 5.0
            },
        {
            'web': False, 'triggered': False, 'trigger_price': 1420.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 
            'stop_price': 1420.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 
            'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTS-5655236', 'mmp': False, 'max_show': 5.0, 
            'last_update_timestamp': 1677903684513, 'label': 'supplyDemandLong60B-closed-1677903684425', 'is_liquidation': False, 
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'sell', 'creation_timestamp': 1677903684513, 'api': True, 'amount': 5.0
            }, 
        {
            'web': False, 'triggered': False, 'trigger_price': 1720.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 
            'stop_price': 1720.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 
            'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTB-5652931', 'mmp': False, 'max_show': 8.0, 
            'last_update_timestamp': 1677473096745, 'label': 'supplyDemandShort60-closed-1677473096', 'is_liquidation': False,
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'buy', 'creation_timestamp': 1677473096745, 'api': True, 'amount': 8.0
            }
        ]
    open_orders = [
        {
            'web': False, 'triggered': False, 'trigger_price': 1720.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 
            'stop_price': 1720.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 
            'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTB-5655271', 'mmp': False, 'max_show': 9.0,
            'last_update_timestamp': 1677934800237, 'label': 'supplyDemandShort60-closed-1677934800137', 'is_liquidation': False, 
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'buy', 'creation_timestamp': 1677934800237, 'api': True, 'amount': 9.0
            }, 
        {
            'web': False, 'triggered': False, 'trigger_price': 1600.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled',
            'stop_price': 1600.0, 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1610.0, 
            'post_only': True, 'order_type': 'take_limit', 'order_state': 'untriggered', 'order_id': 'ETH-TPTS-5655237', 'mmp': False, 'max_show': 5.0,
            'last_update_timestamp': 1677903684561, 'label': 'supplyDemandLong60B-closed-1677903684425', 'is_liquidation': False, 
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'sell', 'creation_timestamp': 1677903684561, 'api': True, 'amount': 5.0
            },
        {
            'web': False, 'triggered': False, 'trigger_price': 1420.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 
            'stop_price': 1420.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 
            'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTS-5655236', 'mmp': False, 'max_show': 5.0, 
            'last_update_timestamp': 1677903684513, 'label': 'supplyDemandLong60B-closed-1677903684425', 'is_liquidation': False, 
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'sell', 'creation_timestamp': 1677903684513, 'api': True, 'amount': 5.0
            }, 
        {
            'web': False, 'triggered': False, 'trigger_price': 1720.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 
            'stop_price': 1720.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 
            'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTB-5652931', 'mmp': False, 'max_show': 8.0, 
            'last_update_timestamp': 1677473096745, 'label': 'supplyDemandShort60-closed-1677473096', 'is_liquidation': False,
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'buy', 'creation_timestamp': 1677473096745, 'api': True, 'amount': 8.0
            }
        ]
    strategies = entries_exits.strategies
    
    for strategy in strategies:
        label_strategy = strategy ['strategy']

        print (strategy)
        if label_strategy == 'supplyDemandLong60A':
            
            index_price = 1550
            is_send_order_allowed = await Strategy.is_send_order_allowed(strategy, index_price, open_trade, open_orders) 

            assert is_send_order_allowed['send_buy_order_allowed'] == False 
            assert is_send_order_allowed['send_sell_order_allowed'] == False
            
        if label_strategy == 'supplyDemandShort60':
            
            index_price = 1550
            is_send_order_allowed = await Strategy.is_send_order_allowed(strategy, index_price, open_trade, open_orders) 
            print (is_send_order_allowed)

            assert is_send_order_allowed['send_buy_order_allowed'] == False
            assert is_send_order_allowed['send_sell_order_allowed'] == False
    