#!/usr/bin/env python
# -*- coding: utf-8 -*-


def telegram_bot_sendtext(bot_message: str, purpose: str = 'general_error') -> str:
    
    """
    # simple telegram
    """
    
    import requests
    if purpose == 'failed_order':
        bot_token   = '1297409216:AAEYu9r7FNd_GQWnxQdM-K6PUSYSQsKuBgE'
        bot_chatID  = '-722130131'#https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id
        
    if purpose == 'general_error':
        bot_token   = '1297409216:AAEYu9r7FNd_GQWnxQdM-K6PUSYSQsKuBgE'
        bot_chatID  = '-439743060'#https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id
    send_text   = 'https://api.telegram.org/bot' + bot_token + (
								'/sendMessage?chat_id=') + bot_chatID + (
							'&parse_mode=HTML&text=') + bot_message
    response    = requests.get(send_text)
    return response.json()