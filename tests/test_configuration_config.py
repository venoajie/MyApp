from src.configuration import config

def test_config ():
        assert [ list(o) for o in[o for o in ([config.main_dotenv ('telegram-failed_order')]) ]][0]  == ['bot_token', 'bot_chatid']
        assert [ list(o) for o in[o for o in ([config.main_dotenv ('deribit-147691')]) ]][0]  == ['type', 
                                                                                                  'user_name', 
                                                                                                  'system_name',
                                                                                                  'client_id',
                                                                                                  'client_secret',
                                                                                                  'id']