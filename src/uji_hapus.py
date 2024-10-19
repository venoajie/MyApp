sub_accounts= [
    {'referrals_count': 0, 'system_name': 'MwaHaHa2020', 'receive_notifications': False, 'email': 'ven.ajie@protonmail.com', 'username': 'MwaHaHa2020', 'margin_model': 'legacy_pm', 'type': 'main', 'id': 147691
     }, 
    {'referrals_count': 0, 
     'system_name': 'MwaHaHa2020_1', 
     'security_keys_enabled': True, 
     'security_keys_assignments': ['account', 'login', 'wallet'], 
     'receive_notifications': False,
     'proof_id_signature': 'Z3VlV_oRH0I9okwS6sSMdH0q8t7kTqnxhZRxg-KuGKztIlG7ULGyEr7Lpwqi3X0Kmvmv_X-cK4FUsQjL1K0qCg', 
     'proof_id': 'UtLdeiQUo0fc44Uoe7s4jtBcqng',
     'login_enabled': False, 
     'is_password': False, 
     'disabled_trading_products': [], 
     'portfolio': {
         'ethw': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.0, 'available_funds': 0.0, 'initial_margin': 0.0, 'maintenance_margin': 0.0, 'equity': 0.0, 'margin_balance': 0.0, 'currency': 'ethw', 'balance': 0.0}, 'sol': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.0, 'available_funds': 0.0, 'initial_margin': 0.0, 'maintenance_margin': 0.0, 'equity': 0.0, 'margin_balance': 0.0, 'currency': 'sol', 'balance': 0.0}, 
         'xrp': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.0, 'available_funds': 0.0, 'initial_margin': 0.0, 'maintenance_margin': 0.0, 'equity': 0.0, 'margin_balance': 0.0, 'currency': 'xrp', 'balance': 0.0}, 'eth': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.04078, 'available_funds': 0.082887, 'initial_margin': 0.006722, 'maintenance_margin': 0.003361, 'equity': 0.04078, 'margin_balance': 0.089608, 'currency': 'eth', 'balance': 0.040788}, 
         'btc': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.001889, 'available_funds': 0.00320698, 'initial_margin': 0.00026007, 'maintenance_margin': 0.00013004, 'equity': 0.00188921, 'margin_balance': 0.00346705, 'currency': 'btc', 'balance': 0.001889}, 'usdt': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.0, 'available_funds': 219.318112, 'initial_margin': 17.785623, 'maintenance_margin': 8.892846, 'equity': 0.0, 'margin_balance': 237.103734, 'currency': 'usdt', 'balance': 0.0}, 
         'usdc': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.0, 'available_funds': 219.340048, 'initial_margin': 17.787402, 'maintenance_margin': 8.893735, 'equity': 0.0, 'margin_balance': 237.127449, 'currency': 'usdc', 'balance': 0.0}, 'steth': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.0, 'available_funds': 0.082973, 'initial_margin': 0.006729, 'maintenance_margin': 0.003364, 'equity': 0.0, 'margin_balance': 0.089702, 'currency': 'steth', 'balance': 0.0}, 
         'matic': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.0, 'available_funds': 0.0, 'initial_margin': 0.0, 'maintenance_margin': 0.0, 'equity': 0.0, 'margin_balance': 0.0, 'currency': 'matic', 'balance': 0.0}, 'eurr': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.0, 'available_funds': 0.0, 'initial_margin': 0.0, 'maintenance_margin': 0.0, 'equity': 0.0, 'margin_balance': 0.0, 'currency': 'eurr', 'balance': 0.0}, 
         'paxg': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.0, 'available_funds': 0.080134, 'initial_margin': 0.006498, 'maintenance_margin': 0.003249, 'equity': 0.0, 'margin_balance': 0.086632, 'currency': 'paxg', 'balance': 0.0}, 'usyc': {'additional_reserve': 0.0, 'spot_reserve': 0.0, 'available_withdrawal_funds': 0.0, 'available_funds': 206.047143, 'initial_margin': 16.709412, 'maintenance_margin': 8.354738, 'equity': 0.0, 'margin_balance': 222.756555, 'currency': 'usyc', 'balance': 0.0}}, 
     'email': 'ven.ajie@protonmail.com', 
     'username': 'MwaHaHa2020_1', 
     'margin_model': 'cross_sm', 
     'type': 'subaccount', 'id': 148510
     }
    ]

print ([o for o in sub_accounts if 148510 == o["id"]][0]['portfolio'])