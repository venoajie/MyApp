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
        self, open_transactions_label: list, strategy_label, type: str = "limit"
    ) -> None:
        """ """
        if open_transactions_label == None:
            open_transactions_label == self.open_orders_from_db

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
                                                                   label,
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
        strategy_label = str_mod.get_strings_before_character(label, "-", 0)
        log.warning (strategy_label)

        get_strategy_int = str_mod.get_strings_before_character(strategy_label, "-", 1)

        label_closed = f"{strategy_label}-closed-{get_strategy_int}"

        main_orders_qty = 0
        main_orders_side =  None
        main_orders_type =  None

        exit_orders_limit_qty = 0
        exit_orders_limit_side = None
        exit_orders_limit_type= None

        exit_orders_market_qty = 0
        exit_orders_market_side = None
        exit_orders_market_type = None
        
        log.info(f'strategy_label {strategy_label}')
        log.info(f'main_side {main_side}')
        log.info(f'net_sum_current_position {net_sum_current_position} {net_sum_current_position} < 0')
        log.info(f'net_sum_open_orders_strategy_market {net_sum_open_orders_strategy_market}')
        
        if main_side == "sell":
            
            # ensure sell side always negative
            max_size = max_size * -1 if max_size > 0 else max_size

            # initial_position
            if net_sum_current_position == 0\
                and  net_sum_open_orders_strategy_limit==0\
                    and net_sum_open_orders_strategy_market==0:
                main_orders_qty = abs(max_size)
                main_orders_side =  'sell'
                main_orders_type = 'limit'
                exit_orders_limit_qty = abs(max_size)
                exit_orders_limit_side = "buy"
                exit_orders_limit_type = "limit"                
                exit_orders_market_qty = abs(max_size)
                exit_orders_market_side = "buy"
                exit_orders_market_type = "stop_market"

            # main has executed
            if net_sum_current_position < 0:
            
                main_orders_qty = 0
                main_orders_side =  None
                order_type_market = "sell"
                if 'hedgingSpot' in strategy_label:
                    if  net_sum_open_orders_strategy_limit==0:
                        exit_orders_limit_qty = abs(net_sum_current_position)
                        exit_orders_limit_side = "buy"
                        exit_orders_limit_type = "limit"                

                        exit_orders_market_qty = 0
                        exit_orders_market_side = None
                        exit_orders_market_type = None
                        
                else:    
                    if  net_sum_open_orders_strategy_limit==0\
                            and net_sum_open_orders_strategy_market !=0:
                        exit_orders_limit_qty = abs(net_sum_current_position)
                        exit_orders_limit_side = "buy"
                        exit_orders_limit_type = "limit"                

                        exit_orders_market_qty = 0
                        exit_orders_market_side = None
                        exit_orders_market_type = "stop_market"
                        
                    if  net_sum_open_orders_strategy_limit!=0\
                            and net_sum_open_orders_strategy_market ==0:
                        exit_orders_limit_qty = 0
                        exit_orders_limit_side = None
                        exit_orders_limit_type = "limit"                

                        exit_orders_market_qty = abs(net_sum_current_position) 
                        exit_orders_market_side = "buy"
                        exit_orders_market_type = "stop_market"

        if main_side == "buy":

            # initial_position
            if net_sum_current_position == 0\
                and  net_sum_open_orders_strategy_limit==0\
                    and net_sum_open_orders_strategy_market==0:
                main_orders_qty =abs(max_size)
                main_orders_side =  'buy'
                exit_orders_limit_qty = abs(max_size)
                exit_orders_limit_side = "sell"
                exit_orders_limit_type = "limit"                
                exit_orders_market_qty = abs(max_size)
                exit_orders_market_side = "sell"
                exit_orders_market_type = 'stop_market'
                
                
            # main has execute
            if net_sum_current_position > 0:
                main_orders_qty = 0
                main_orders_side =  None
                order_type_market = "sell"
                
                if net_sum_open_orders_strategy_limit==0\
                        and net_sum_open_orders_strategy_market!= 0:
                    exit_orders_limit_qty = abs(net_sum_current_position)
                    exit_orders_limit_side = "sell"
                    exit_orders_limit_type = "limit"                
                    exit_orders_market_qty = 0
                    exit_orders_market_side = None
                    exit_orders_market_type = "stop_market"
                
                if net_sum_open_orders_strategy_limit!=0\
                        and net_sum_open_orders_strategy_market== 0:
                    exit_orders_limit_qty = 0
                    exit_orders_limit_side = None
                    exit_orders_limit_type = "limit"                
                    exit_orders_market_qty = abs(net_sum_current_position)
                    exit_orders_market_side = "sell"
                    exit_orders_market_type = "stop_market"
                
        return {
            "main_orders_qty": main_orders_qty,
            "main_orders_side": main_orders_side,
            'main_orders_type':  main_orders_type,
            "exit_orders_limit_qty": exit_orders_limit_qty,
            "exit_orders_limit_side": exit_orders_limit_side,
            "exit_orders_limit_type": exit_orders_limit_type,
            "exit_orders_market_qty": exit_orders_market_qty,
            "exit_orders_market_side": exit_orders_market_side,
            "exit_orders_market_type": exit_orders_market_type,
            "label_closed": label_closed,
            
        }
            