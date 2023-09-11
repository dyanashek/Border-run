import telebot
import requests
import datetime
import time
import gspread

import keyboards
import config
import text
import db_functions


bot = telebot.TeleBot(config.TELEGRAM_TOKEN)


def connect_ai(change_id, question, message_to_reply, history, user_id):
    """Connects to AI, handles query."""

    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'User-Agent': 'python-requests/2.31.0',
        'accept': 'application/json',
        'token': config.AI_TOKEN,
    }

    json_data = {
        'question' : question,
        'chat_history' : history,
    }

    try:
        response = requests.post(config.AI_ENDPOINT, headers=headers, json=json_data, timeout=30)

        if response.status_code == 200:
            answer = response.json()[0].get('data').get('answer')

            history_question = {
                'sent' : True,
                'message' : question,
            }

            history_answer= {
                'sent' : False,
                'message' : answer,
            }

            history.append(history_question)
            history.append(history_answer)

        else:
            answer = False
            history = False

    except:
        answer = False
        history = False


    if answer and history:
        db_functions.update_history(user_id, str(history))

        for i in range(1, 20):
            answer = answer.replace(f'{i}.', f'\n\n{i}.')

        answer = answer.replace('- ', '\n- ')

        try:
            bot.delete_message(chat_id=user_id,
                               message_id=change_id,
                               )
            
            bot.send_message(chat_id=user_id,
                            text=answer,
                            reply_markup=keyboards.book_keyboard(),
                            reply_to_message_id=message_to_reply
                            )
        except:
            pass
    
    else:
        try:
            bot.delete_message(chat_id=user_id,
                               message_id=change_id,
                               )
            
            bot.send_message(chat_id=user_id,
                            text=text.ERROR_TEXT,
                            parse_mode='Markdown',
                            )
        except:
            pass
        
    
    db_functions.set_busy(user_id, False)


def p2p_bybit(currency = 'THB', amount = ''):
    """Gets price of buying or selling usdt on Binance p2p."""

    # indicate trade side
    side = '1'
    if currency == 'THB':
        side = '0'
    
    pay_types = []
    if currency == 'RUB':
        pay_types = ['64', '75', '14']
    elif currency == 'THB':
        pay_types = ['14']

    # construct params
    data_binance = {
        "tokenId": 'USDT',
        "currencyId": currency,
        "authMaker" : "true",
        "side": side,
        "amount": amount,
        "payment" : pay_types,
        "userId" : "",
    }
    # make a request
    try:
        deals = requests.post(url=config.URL_BYBIT, data=data_binance, headers=config.HEADERS).json().get('result').get('items')
    except:
        deals = None
    
    if deals is not None:

        for deal in deals:
            # extract merchants order count and rate
            order_count = int(deal.get('recentOrderNum'))
            finish_rate = float(deal.get('recentExecuteRate'))

            # extract price if the merchant fits params
            if order_count >= config.ORDERS and finish_rate >= config.ORDERS_RATE:
                price = float(deal.get('price'))

                return price


def get_exchange_rate():
    """Gets minimal rate for currency pair."""

    thb_price = p2p_bybit()

    rub_price = p2p_bybit('RUB')
    rate = round((rub_price / thb_price) * config.COEFF, 3)


    return rate


def cancel_unpaid():
    while True:
        if (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).hour >= 17:
            bookings_ids = db_functions.select_unpaid()
            for booking_id in bookings_ids:
                db_functions.update_booking_field(booking_id, 'status', 'canceled')
                booking_info = db_functions.get_booking_info(booking_id)
                client_id = db_functions.get_booking_field(booking_id, 'user_id')

                try:
                    bot.send_message(chat_id=client_id,
                                     text=text.unpaid_booking_declined(booking_id, *booking_info),
                                     parse_mode='Markdown',
                                     disable_notification=False,
                                     )
                except:
                    pass
        
        time.sleep(30)


def update_finished():
    while True:
        db_functions.update_finished_status()
        time.sleep(30)


def get_account_info():
    while True:
        try:
            service_acc = gspread.service_account(filename='service_account.json')
            sheet = service_acc.open(config.SPREAD_NAME)
            work_sheet = sheet.worksheet(config.LIST_NAME)

            account_info = work_sheet.get_all_values()[-1]

            config.BANK =  account_info[0]
            config.ACCOUNT = account_info[1]
            config.NUMBER = account_info[2]
            config.RECEIVER = account_info[3]
        except:
            pass

        time.sleep(300)


def send_marketing_message(text, content_type, media_id=None):
    users_ids = db_functions.get_all_users_ids()

    for user_id in users_ids:
        if content_type == 'text':
            try:
                bot.send_message(chat_id=user_id,
                                 text=text,
                                 disable_notification=False,
                                 )
            except:
                pass

        elif content_type == 'photo':
            try:
                bot.send_photo(chat_id=user_id,
                               caption=text,
                               photo=media_id,
                               disable_notification=False,
                               )
            except:
                pass

        elif content_type == 'video':
            try:
                bot.send_video(chat_id=user_id,
                               caption=text,
                               video=media_id,
                               disable_notification=False,
                               )
            except:
                pass


def inform_needed_new_booking():
    while True:
        bookings_ids = db_functions.get_needed_new_booking()

        for booking_id in bookings_ids:
            client_id = db_functions.get_booking_field(booking_id, 'user_id')

            try:
                bot.send_message(chat_id=client_id,
                                 text=text.NEED_NEW_BORDER,
                                 reply_markup=keyboards.book_keyboard(),
                                 parse_mode='Markdown',
                                 disable_notification=False,
                                 )
                db_functions.update_booking_field(booking_id, 'informed', True)

            except:
                pass

        time.sleep(28800)