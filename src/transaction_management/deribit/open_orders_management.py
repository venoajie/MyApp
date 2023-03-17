# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from loguru import logger as log

# user defined formula
from utilities import (
    pickling,
    system_tools,
    number_modification,
    string_modification as str_mod
)


def catch_error(error, idle: int = None) -> list:
    """ """
    system_tools.catch_error_message(error, idle)


def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    from utilities import telegram_app

    return telegram_app.telegram_bot_sendtext(bot_message, purpose)


@dataclass(unsafe_hash=True, slots=True)
class MyOrders:

    """

    +----------------------------------------------------------------------------------------------+
    #  clean up open orders data

    Convention: negative sign = short, vv
    """

    open_orders_from_db: list

    def open_orders_all(self) -> list:
        """ """
        none_data = [None, []]
        return [] if self.open_orders_from_db in none_data else self.open_orders_from_db

    def open_orders_api(self) -> list:
        """ """
        return (
            []
            if self.open_orders_all() == []
            else [o for o in self.open_orders_all() if o["api"] == True]
        )

    def open_orders_manual(self) -> list:
        """ """
        return (
            []
            if self.open_orders_all() == []
            else [o for o in self.open_orders_all() if o["api"] == False]
        )

    def open_orders_status(self, status) -> list:
        """ """

        none_data = [None, []]

        try:
            trade_seq = [o["trade_seq"] for o in self.open_orders_all()]
            orders_status = [o for o in self.open_orders_all() if o["state"] == status]
        except:
            orders_status = [
                o for o in self.open_orders_all() if o["order_state"] == status
            ]

        return [] if self.open_orders_all() in none_data else orders_status

    def open_orders_api_basedOn_label(self, label: str) -> list:
        """ """

        return (
            []
            if self.open_orders_api() == []
            else [o for o in self.open_orders_api() if label in o["label"]]
        )

    def open_orders_api_last_update_timestamps(self) -> list:
        """ """
        return (
            []
            if self.open_orders_api() == []
            else [o["last_update_timestamp"] for o in self.open_orders_api()]
        )

    def open_orders_api_basedOn_label_last_update_timestamps(self, label: str) -> list:
        """ """
        return (
            []
            if self.open_orders_api_basedOn_label(label) == []
            else [
                o["last_update_timestamp"]
                for o in self.open_orders_api_basedOn_label(label)
            ]
        )

    def open_orders_api_basedOn_label_last_update_timestamps_min(
        self, label: str
    ) -> list:
        """ """

        return (
            []
            if self.open_orders_api_basedOn_label_last_update_timestamps(label) == []
            else min(self.open_orders_api_basedOn_label_last_update_timestamps(label))
        )

    def open_orders_api_basedOn_label_last_update_timestamps_max(
        self, label: str
    ) -> list:
        """ """

        return (
            []
            if self.open_orders_api_basedOn_label_last_update_timestamps(label) == []
            else max(self.open_orders_api_basedOn_label_last_update_timestamps(label))
        )

    def open_orders_api_basedOn_label_last_update_timestamps_min_id(
        self, label: str
    ) -> list:
        """ """

        return (
            []
            if self.open_orders_api_basedOn_label_last_update_timestamps(label) == []
            else (
                [
                    o["order_id"]
                    for o in self.open_orders_api_basedOn_label(label)
                    if o["last_update_timestamp"]
                    == self.open_orders_api_basedOn_label_last_update_timestamps_min(
                        label
                    )
                ]
            )[0]
        )

    def open_orders_api_basedOn_label_last_update_timestamps_max_id(
        self, label: str
    ) -> list:
        """ """

        return (
            []
            if self.open_orders_api_basedOn_label_last_update_timestamps(label) == []
            else (
                [
                    o["order_id"]
                    for o in self.open_orders_api_basedOn_label(label)
                    if o["last_update_timestamp"]
                    == self.open_orders_api_basedOn_label_last_update_timestamps_max(
                        label
                    )
                ]
            )[0]
        )

    def open_orders_api_basedOn_label_items_qty(self, label: str) -> list:
        """ """
        return (
            []
            if self.open_orders_api_basedOn_label(label) == []
            else len([o for o in self.open_orders_api_basedOn_label(label)])
        )

    def open_orders_api_basedOn_label_items_net(
        self, label: str = None
    ) -> list:  #! inconsistent output comparing to other funcs.
        """ """

        if label == None:
            result = (
                0
                if self.open_orders_api() == []
                else self.net_sum_order_size(self.open_orders_api())
            )

        else:
            # log.debug (self.open_orders_api () )
            result = (
                0
                if self.open_orders_api_basedOn_label(label) == []
                else self.net_sum_order_size(
                    [o for o in self.open_orders_api_basedOn_label(label)]
                )
            )

        return result

    def net_sum_order_size(self, selected_transactions: list) -> float:
        """ """
        return number_modification.net_position(selected_transactions)

    def open_orders_api_basedOn_label_items_size(self, label: str) -> list:
        """ """
        return (
            []
            if self.open_orders_api_basedOn_label(label) == []
            else self.net_sum_order_size(self.open_orders_api_basedOn_label(label))
        )

    def recognizing_order(self, order: dict) -> dict:
        """

        Captured some order attributes

        Args:
            order (dict): Order from exchange.

        Returns:
            dict: explaining order state and order id.

        """

        try:
            log.info(order)  # log the order to the log file

            if "trade_seq" not in order:
                # get the order id
                order_id = order["order_id"]

                # get the order state
                order_state = order["order_state"]

            if "trade_seq" in order:
                # get the order id
                order_id = order["order_id"]

                # get the order state
                order_state = order["state"]

        except Exception as error:
            catch_error(error)

        return {
            "order_state_open": order_state == "open",
            "order_state_else": order_state != "open",
            "order_id": order_id,
        }

    def combine_open_orders_based_on_id(
        self, open_orders_open: list, order_id: str
    ) -> dict:
        """ """
        return {
            "item_with_same_id": [
                o for o in open_orders_open if o["order_id"] == order_id
            ],
            "item_with_diff_id": [
                o for o in open_orders_open if o["order_id"] != order_id
            ],
        }

    def compare_open_order_per_db_vs_get(
        self, open_orders_from_sub_account_get: list
    ) -> int:
        """ """

        try:
            both_sources_are_equivalent = (
                open_orders_from_sub_account_get == self.open_orders_from_db
            )
            # log.critical (f'both_sources_are_equivalent {both_sources_are_equivalent} open_order_from_get {open_orders_from_sub_account_get} open_order_from_db {self. open_orders_from_db}')

            if both_sources_are_equivalent == False:
                info = f"OPEN ORDER DIFFERENT open_order_from_get \
                        {open_orders_from_sub_account_get}  \
                            open_order_from_db \
                                {self. open_orders_from_db} \n "
                telegram_bot_sendtext(info)
            # log.warning (f'difference {difference}')

            return both_sources_are_equivalent

        except Exception as error:
            catch_error(error)

    def open_orderLabelCLosed(self, open_orders: list = None) -> list:
        """
        Get order with closed labels  but have no open labels  pair
        The result should be further compared to open trades with open labels
        """

        if open_orders == None:
            open_orders = self.open_orders_from_db

        # get order with open labels
        order_label_open = [
            str_mod.extract_integers_from_text(o["label"])
            for o in open_orders
            if "open" in (o["label"])
        ]

        # furthermore, extract order with closed label but not
        # registered in open labels above

        order_label_closed = [
            str_mod.extract_integers_from_text(o["label"])
            for o in open_orders
            if "closed" in (o["label"])
            and str_mod.extract_integers_from_text(o["label"]) not in order_label_open
        ]

        # log.error (str_mod.remove_redundant_elements (order_label_closed))
        # remove redundant labels
        return str_mod.remove_redundant_elements(order_label_closed)

    def distribute_order_transactions(self, currency) -> None:
        """ """

        from loguru import logger as log

        my_path_orders_open = system_tools.provide_path_for_file(
            "orders", currency, "open"
        )
        try:
            if self.open_orders_from_db:
                log.debug(self.open_orders_from_db)

                for order in self.open_orders_from_db:
                    order_state = self.recognizing_order(order)
                    log.critical(order_state)

                    if order_state["order_state_open"]:
                        log.error("ORDER_STATE OPEN")
                        log.info(f"{order=}")

                        pickling.append_and_replace_items_based_on_qty(
                            my_path_orders_open, order, 1000, True
                        )

                    if order_state["order_state_else"]:
                        my_path_orders_else = system_tools.provide_path_for_file(
                            "orders", currency, "else"
                        )
                        log.critical("ORDER_STATE ELSE")
                        log.info(f"{order=}")
                        log.critical(f"{order_state=}")
                        log.critical(f"{my_path_orders_else=}")

                        order_id = order_state["order_id"]

                        open_orders_open = pickling.read_data(my_path_orders_open)

                        item_in_open_orders_open = self.combine_open_orders_based_on_id(
                            open_orders_open, order_id
                        )
                        log.info(f"{open_orders_open=}")
                        log.debug(f"{item_in_open_orders_open=}")

                        item_with_same_id = item_in_open_orders_open[
                            "item_with_same_id"
                        ]
                        item_with_diff_id = item_in_open_orders_open[
                            "item_with_diff_id"
                        ]

                        pickling.append_and_replace_items_based_on_qty(
                            my_path_orders_else, order, 1000, True
                        )

                        if item_with_same_id != []:
                            pickling.append_and_replace_items_based_on_qty(
                                my_path_orders_else, item_with_same_id, 100000, True
                            )

                        pickling.replace_data(
                            my_path_orders_open, item_with_diff_id, True
                        )

            else:
                pickling.replace_data(my_path_orders_open, [], True)

        except Exception as error:
            catch_error(error)

    def transactions_label_strategy(
        self, open_transactions_label, strategy_label
    ) -> None:
        """ """

        try:
            result = [
                o
                for o in open_transactions_label
                if strategy_label in str_mod.get_strings_before_character(o["label"])
            ]
        except:
            result = []

        return result

    def trade_based_on_label_strategy(
        self, open_transactions_label, strategy_label, type: str = "limit"
    ) -> None:
        """ """

        transactions = self.transactions_label_strategy(
            open_transactions_label, strategy_label
        )
        #log.warning (strategy_label)
        #log.critical (f'transactions {transactions}')
        #log.warning (open_transactions_label)

        return {
            "net_sum_order_size": []
            if transactions == []
            else self.net_sum_order_size(transactions),
            "len_transactions": [] if transactions == [] else len(transactions),
            "transaction_label_strategy_type": []
            if transactions == []
            else ([o for o in transactions if type in o["order_type"]]),
            "instrument": []
            if transactions == []
            else [o["instrument_name"] for o in transactions][0],
        }

    def calculate_order_size_and_side_for_outstanding_transactions(self,
                                                                   main_side: str, 
                                                                   net_sum_current_position: float,
                                                                   net_sum_open_orders_strategy_limit: int, 
                                                                   net_sum_open_orders_strategy_market: int, 
                                                                   max_size: float
                                                                   ):

        """
        Compute order size attributes based on its position, order, and strategy setting
        Convention: 
            input: negative sign = short, vv
            output: all positive
        
        Args:
            main_side (str): side as provided by the strategy configuration
            max_size (float): size as per position sizing
            net_sum_current_position (float): sum myTradebuy - sum myTrade sell
            net_sum_open_orders_strategy_limit (float): sum open orders buy - sum open orders sell, type - limit
            net_sum_open_orders_strategy_market (float): sum open orders buy - sum open orders sell, type - market
            
        Returns:
            dict

        """
        
        # most strategies have TP (limit) & SL (market) orders
        
        # current position vs open order limit
        positions_covered_by_limit_orders = net_sum_current_position - net_sum_open_orders_strategy_limit
        
        # current position vs open order market
        positions_covered_by_market_orders = net_sum_current_position - net_sum_open_orders_strategy_market
        
        main_orders_sum_vs_max_orders = max_size - net_sum_current_position

        main_orders_qty = 0
        main_orders_side =  None
        exit_orders_limit_qty = 0
        exit_orders_limit_side = None
        exit_orders_market_qty = 0
        exit_orders_market_side = None
        
        if main_side == "sell":
            
            # ensure sell side always negative
            max_size = max_size * -1 if max_size > 0 else max_size

            # initial_position
            if net_sum_current_position == 0\
                and  net_sum_open_orders_strategy_limit==0\
                    and net_sum_open_orders_strategy_market==0:
                main_orders_qty = abs(max_size)
                main_orders_side =  'sell'
                exit_orders_limit_qty = abs(max_size)
                exit_orders_limit_side = "buy"
                exit_orders_market_qty = abs(max_size)
                exit_orders_market_side = "buy"

            # main has executed
            if net_sum_current_position < 0:
            
                main_orders_qty = 0
                main_orders_side =  None
                if  net_sum_open_orders_strategy_limit==0\
                        and net_sum_open_orders_strategy_market !=0:
                    exit_orders_limit_qty = abs(net_sum_current_position)
                    exit_orders_limit_side = "buy"
                    exit_orders_market_qty = 0
                    exit_orders_market_side = None
                    
                if  net_sum_open_orders_strategy_limit!=0\
                        and net_sum_open_orders_strategy_market ==0:
                    exit_orders_limit_qty = 0
                    exit_orders_limit_side = None
                    exit_orders_market_qty = abs(net_sum_current_position) 
                    exit_orders_market_side = "buy"

        if main_side == "buy":

            # initial_position
            if net_sum_current_position == 0\
                and  net_sum_open_orders_strategy_limit==0\
                    and net_sum_open_orders_strategy_market==0:
                main_orders_qty =abs(max_size)
                main_orders_side =  'buy'
                exit_orders_limit_qty = abs(max_size)
                exit_orders_limit_side = "sell"
                exit_orders_market_qty = abs(max_size)
                exit_orders_market_side = "sell"
                
            # main has execute
            if net_sum_current_position > 0:
                main_orders_qty = 0
                main_orders_side =  None
                
                if net_sum_open_orders_strategy_limit==0\
                        and net_sum_open_orders_strategy_market!= 0:
                    exit_orders_limit_qty = abs(net_sum_current_position)
                    exit_orders_limit_side = "sell"
                    exit_orders_market_qty = 0
                    exit_orders_market_side = None
                
                if net_sum_open_orders_strategy_limit!=0\
                        and net_sum_open_orders_strategy_market== 0:
                    exit_orders_limit_qty = 0
                    exit_orders_limit_side = None
                    order_type_limit = "sell"
                    exit_orders_market_qty = abs(net_sum_current_position)
                    exit_orders_market_side = "sell"
                    order_type_market = "sell"
                
        return {
            "main_orders_qty": main_orders_qty,
            "main_orders_side": main_orders_side,
            "exit_orders_limit_qty": exit_orders_limit_qty,
            "exit_orders_limit_side": exit_orders_limit_side,
            "order_type_market": order_type_market,
            "exit_orders_market_qty": exit_orders_market_qty,
            "exit_orders_market_side": exit_orders_market_side,
            "order_type_limit": order_type_limit,
        }
            
    def determine_order_size_and_side_for_outstanding_transactions(
        self,
        strategy_label_from_outstanding_transactions: str,
        net_sum_current_position: int,
        max_size: int,
    ) -> None:
        """
        Determine order size based on current position size vs current position
        - Additional main order size
        - Exit order size
        - Side for every order size

        Args:
            net_sum_current_position (int): sum myTradebuy - sum myTrade sell
            strategy_label_from_outstanding_transactions (str): taken from o/s my trades label (format example = supplyDemandShort60)

        Returns:
            dict

        Example:
            data_original = 'hedgingSpot-open-1671189554374' become 'hedgingSpot'

        """
        from strategies import entries_exits

        strategies = entries_exits.strategies

        try:
            # result: 'hedgingSpot'/'supplyDemandShort60'
            basic_strategy = str_mod.get_strings_before_character(
                strategy_label_from_outstanding_transactions, "-", 0
            )

            side_basic_strategy = [
                o for o in strategies if basic_strategy in o["strategy"]
            ][0]["side"]

            # result: 'hedgingSpot'/'supplyDemandShort60'
            label_basic_strategy = [
                o for o in strategies if basic_strategy in o["strategy"]
            ][0]["strategy"]

            # default result for order_type_market
            order_type_market = False
            
            open_orders_from_db = self.open_orders_from_db
            open_orders_strategy_limit = self.trade_based_on_label_strategy(open_orders_from_db,label_basic_strategy,'limit')
            open_orders_strategy_market = self.trade_based_on_label_strategy(open_orders_from_db,label_basic_strategy,'market')
            net_sum_open_orders_strategy_limit = open_orders_strategy_limit['net_sum_order_size']
            net_sum_open_orders_strategy_limit = 0 if net_sum_open_orders_strategy_limit == [] else net_sum_open_orders_strategy_limit

            net_sum_open_orders_strategy_market =  open_orders_strategy_market['net_sum_order_size']
            net_sum_open_orders_strategy_market = 0 if net_sum_open_orders_strategy_market == [] else net_sum_open_orders_strategy_market

            #! same result/recheck:
            log.warning (f'label_basic_strategy {label_basic_strategy}')
            log.warning (f'basic_strategy {basic_strategy}')
            log.warning (f'net_sum_open_orders_strategy_limit {net_sum_open_orders_strategy_limit} open_orders_strategy_limit {open_orders_strategy_limit} ')
            log.warning (f'net_sum_open_orders_strategy_market {net_sum_open_orders_strategy_market} open_orders_strategy_market {open_orders_strategy_market} ')
            positions_covered_by_limit_orders = net_sum_current_position - net_sum_open_orders_strategy_limit
            positions_covered_by_market_orders = net_sum_current_position - net_sum_open_orders_strategy_market
            # log.warning (f'basic_strategy {basic_strategy}')
            # log.warning (f'label_basic_strategy {label_basic_strategy}')
            # log.warning (f'strategy_label_from_outstanding_transactions {strategy_label_from_outstanding_transactions}')

            if side_basic_strategy == "sell":
                calculate_order_size_and_side= self.calculate_order_size_and_side_for_outstanding_transactions(
                                                                   side_basic_strategy, 
                                                                   net_sum_current_position,
                                                                   net_sum_open_orders_strategy_limit, 
                                                                   net_sum_open_orders_strategy_market, 
                                                                   max_size
                                                                   )
                # sell side is always negative
                max_size = max_size * -1 if max_size > 0 else max_size

                main_orders_sum_vs_max_orders = max_size - net_sum_current_position
                
                log.error (f'positions_covered_by_limit_orders {positions_covered_by_limit_orders}')
                #log.error (f'max_size {max_size}')
                #log.error (f'net_sum_current_position {net_sum_current_position}')
                
                # net sell positions > net order
                if positions_covered_by_limit_orders < 0:
                    remain_main_orders = 0
                    excess_position = main_orders_sum_vs_max_orders
                    remain_exit_orders = net_sum_current_position - net_sum_open_orders_strategy_limit
                    side = "buy"

                if main_orders_sum_vs_max_orders < 0:
                    remain_main_orders = main_orders_sum_vs_max_orders
                    remain_exit_orders = 0
                    excess_position = 0
                    side = "sell"

                if main_orders_sum_vs_max_orders == 0:
                    remain_main_orders = 0
                    remain_exit_orders = 0
                    excess_position = 0
                    side = None

            if side_basic_strategy == "buy":
                
                calculate_order_size_and_side= self.calculate_order_size_and_side_for_outstanding_transactions(
                                                                   side_basic_strategy, 
                                                                   net_sum_current_position,
                                                                   net_sum_open_orders_strategy_limit, 
                                                                   net_sum_open_orders_strategy_market, 
                                                                   max_size
                                                                   )
                main_orders_sum_vs_max_orders = net_sum_current_position - max_size

                if main_orders_sum_vs_max_orders > 0:
                    remain_main_orders = 0
                    remain_exit_orders = -main_orders_sum_vs_max_orders
                    excess_position = -main_orders_sum_vs_max_orders
                    side = "sell"

                if main_orders_sum_vs_max_orders < 0:
                    remain_main_orders = abs(main_orders_sum_vs_max_orders)
                    remain_exit_orders = 0
                    excess_position = 0
                    side = "buy"

                if main_orders_sum_vs_max_orders == 0:
                    remain_main_orders = 0
                    remain_exit_orders = 0
                    excess_position = 0
                    side = None

            
            len_open_order_label_strategy_type_market = []
            len_open_order_label_strategy_type_limit = []

            log.critical(label_basic_strategy)
            # log.warning (open_orders_from_db ==[])
            # log.warning (open_orders_from_db)
            if open_orders_from_db == []:
                order_type_market = True

            else:
                # get open order with the respective strategy and order type take_limit
                # to optimise the profit, using take_limit as order type default order
                open_order_label_strategy_type_limit = (
                    self.trade_based_on_label_strategy(
                        open_orders_from_db, basic_strategy, "limit"
                    )
                )
                len_open_order_label_strategy_type_limit = (
                    open_order_label_strategy_type_limit["len_transactions"]
                )

                # get open order with the respective strategy and order type stop market
                # to reduce the possibility of order not executed, stop loss using
                # stop market as order type default order
                open_order_label_strategy_type_market = (
                    self.trade_based_on_label_strategy(
                        open_orders_from_db, basic_strategy, "stop_market"
                    )
                )
                len_open_order_label_strategy_type_market = (
                    open_order_label_strategy_type_market["len_transactions"]
                )

                # log.warning (f'len_open_order_label_strategy_type_market {len_open_order_label_strategy_type_market}')
                # log.warning ('hedgingSpot' in label_basic_strategy)
                # log.warning (f'len_open_order_label_strategy_type_market {len_open_order_label_strategy_type_market == []}')
                # log.warning (f'len_open_order_label_strategy_type_market {len_open_order_label_strategy_type_market < 1}')

                order_type_market = (
                    False
                    if "hedgingSpot" in label_basic_strategy
                    else True
                    if len_open_order_label_strategy_type_market == []
                    else len_open_order_label_strategy_type_market < 1
                )

            return {'calculate_order_size_and_side': calculate_order_size_and_side,
                "remain_main_orders": remain_main_orders,
                "excess_position": excess_position,
                "remain_exit_orders": remain_exit_orders,
                "no_limit_open_order_outstanding": len_open_order_label_strategy_type_limit
                == [],
                "no_market_open_order_outstanding": len_open_order_label_strategy_type_limit
                == [],
                "order_type_market": order_type_market,
                "order_type_limit": True
                if len_open_order_label_strategy_type_limit == []
                else len_open_order_label_strategy_type_limit < 1,
                "side": side,
            }

        except Exception as error:
            catch_error(error)
