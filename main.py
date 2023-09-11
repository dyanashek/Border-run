import telebot
import logging
import threading
import datetime

import config
import utils
import functions
import keyboards
import text
import db_functions

logging.basicConfig(level=logging.ERROR, 
                    filename="py_log.log", 
                    filemode="w", 
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    )

bot = telebot.TeleBot(config.TELEGRAM_TOKEN, disable_notification=True)


threading.Thread(daemon=True, target=functions.cancel_unpaid).start()
threading.Thread(daemon=True, target=functions.update_finished).start()
threading.Thread(daemon=True, target=functions.get_account_info).start()
threading.Thread(daemon=True, target=functions.inform_needed_new_booking).start()


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = str(message.from_user.id)

    if not db_functions.is_in_database(user_id):
        user_username = message.from_user.username
        db_functions.add_user(user_id, user_username)

    bot.send_message(chat_id=message.chat.id,
                    text=text.START_TEXT,
                    reply_markup=keyboards.book_keyboard(),
                    parse_mode='Markdown',
                    )
    

@bot.message_handler(commands=['cancel'])
def start_message(message):
    message_id = db_functions.get_message_id(message.from_user.id)

    try:
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message_id,
                           )
    except:
        pass

    db_functions.set_busy(message.from_user.id, False)

    bot.send_message(chat_id=message.chat.id,
                     text=text.CANCELED_REQUESTS,
                     )


@bot.message_handler(commands=['reload'])
def start_message(message):
    db_functions.update_history(message.from_user.id, '[]')

    bot.send_message(chat_id=message.chat.id,
                     text=text.CLEAR_HISTORY,
                     )


@bot.message_handler(commands=['cancel_slip'])
def start_message(message):
    user_id = message.from_user.id

    input_data = db_functions.get_user_field_info(user_id, 'input_data')

    if input_data and 'payment' in input_data:
        db_functions.update_user_field(user_id, 'input_data', None)

        bot.send_message(chat_id=message.chat.id,
                         text=text.INPUT_CANCELED,
                         parse_mode='Markdown',
                         )


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(chat_id=message.chat.id,
                     text=text.HELP_MESSAGE,
                     parse_mode='Markdown',
                     )


@bot.callback_query_handler(func = lambda call: True)
def callback_query(call):
    """Handles queries from inline keyboards."""

    # getting message's and user's ids
    message_id = call.message.id
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    call_data = call.data.split('_')
    query = call_data[0]

    if query == 'route':
        booking_id = int(call_data[1])
        route = call_data[2]

        booking_status = db_functions.get_booking_field(booking_id, 'status')

        if booking_status and booking_status == 'creating':
            db_functions.update_booking_field(booking_id, 'route', route)

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.ANSWER_DATA,
                                  parse_mode='Markdown',
                                  )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=keyboards.current_month_keyboard(route, booking_id),
                                          )

        else:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.OUTDATED,
                                  parse_mode='Markdown',
                                  )
    
    elif query == 'next':
        year = int(call_data[1])
        month = int(call_data[2])
        route = call_data[3]
        booking_id = int(call_data[4])
         
        bot.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=keyboards.next_month_keyboard(year, month, route, booking_id),
                                        )

    elif query == 'prev':
        route = call_data[1]
        booking_id = int(call_data[2])
           
        bot.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=keyboards.current_month_keyboard(route, booking_id),
                                        )

    elif query == 'date':
        route = call_data[1]
        year = int(call_data[2])
        month = int(call_data[3])
        day = int(call_data[4])
        booking_id = int(call_data[5])

        booking_status = db_functions.get_booking_field(booking_id, 'status')

        if booking_status and (booking_status == 'creating' or booking_status == 'created'):
            deadline = datetime.datetime(year=year, month=month, day=day, hour=config.LAST_HOUR - 1) - datetime.timedelta(days=1)
            curr_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

            if deadline > curr_time:
                db_functions.update_booking_field(booking_id, 'book_date', datetime.date(year=year, month=month, day=day))

                if booking_status == 'creating':
                    bot.edit_message_text(chat_id=chat_id,
                                          message_id=message_id,
                                          text=text.ANSWER_COUNT,
                                          parse_mode='Markdown',
                                          )
                    
                    bot.edit_message_reply_markup(chat_id=chat_id,
                                                  message_id=message_id,
                                                  reply_markup=keyboards.count_keyboard(booking_id),
                                                  )
                else:
                    db_functions.update_user_field(user_id, 'input_data', None)
                    booking_info = db_functions.get_booking_info(booking_id)

                    try:
                        bot.delete_message(chat_id=chat_id, message_id=message_id)
                    except:
                        pass

                    names = eval(booking_info[5])
                    passport_photos = eval(booking_info[6])
                    stamp_photos = eval(booking_info[7])

                    for index in range(len(names)):
                        group_media = [telebot.types.InputMediaPhoto(passport_photos[index]), telebot.types.InputMediaPhoto(stamp_photos[index])]

                        bot.send_media_group(chat_id=chat_id,
                                            media=group_media,
                                            timeout=30,
                                            )

                    bot.send_message(chat_id=chat_id,
                                    text=text.booking_info(booking_id, *booking_info),
                                    reply_markup=keyboards.change_keyboard(booking_id),
                                    parse_mode='Markdown',
                                    )

            else:
                bot.edit_message_reply_markup(chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=keyboards.current_month_keyboard(route, booking_id),
                                        )

        else:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.OUTDATED,
                                  parse_mode='Markdown',
                                  )

    elif query == 'count':
        booking_id = int(call_data[1])
        count = int(call_data[2])

        booking_status = db_functions.get_booking_field(booking_id, 'status')

        if booking_status and booking_status == 'creating':
            db_functions.update_booking_field(booking_id, 'count', count)

            db_functions.update_user_field(user_id, 'input_data', f'name_{booking_id}')

            alone = False
            if count == 1:
                alone = True

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.ask_name(alone, 0),
                                  parse_mode='Markdown',
                                  )

        else:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.OUTDATED,
                                  parse_mode='Markdown',
                                  )

    elif query == 'change':
        subject = call_data[1]
        booking_id = int(call_data[2])

        if subject == 'date':
            route = db_functions.get_booking_field(booking_id, 'route')

            bot.edit_message_text(chat_id=chat_id,
                                  text=text.ANSWER_DATA,
                                  message_id=message_id,
                                  parse_mode='Markdown',
                                  )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=keyboards.current_month_keyboard(route, booking_id),
                                          )

        elif subject == 'name':
            db_functions.update_user_field(user_id, 'input_data', f'name_{booking_id}')
            db_functions.update_booking_field(booking_id, 'names', '[]')

            count = db_functions.get_booking_field(booking_id, 'count')

            alone = False
            if count == 1:
                alone = True

            bot.edit_message_text(chat_id=chat_id,
                                  text=text.ask_name(alone, 0),
                                  message_id=message_id,
                                  parse_mode='Markdown',
                                  )

        elif subject == 'passport':
            db_functions.update_user_field(user_id, 'input_data', f'passport_photos_{booking_id}')
            db_functions.update_booking_field(booking_id, 'passport_photos', '[]')

            count = db_functions.get_booking_field(booking_id, 'count')
            names = eval(db_functions.get_booking_field(booking_id, 'names'))

            alone = False
            if count == 1:
                alone = True

            bot.edit_message_text(chat_id=chat_id,
                                  text=text.ask_passport_photos(alone, names[0]),
                                  message_id=message_id,
                                  parse_mode='Markdown',
                                  )

        elif subject == 'stamp':
            db_functions.update_user_field(user_id, 'input_data', f'stamp_photos_{booking_id}')
            db_functions.update_booking_field(booking_id, 'stamp_photos', '[]')

            count = db_functions.get_booking_field(booking_id, 'count')
            names = eval(db_functions.get_booking_field(booking_id, 'names'))

            alone = False
            if count == 1:
                alone = True

            bot.edit_message_text(chat_id=chat_id,
                                  text=text.ask_stamp_photos(alone, names[0]),
                                  message_id=message_id,
                                  parse_mode='Markdown',
                                  )

        elif subject == 'phone':
            db_functions.update_user_field(user_id, 'input_data', f'phone_{booking_id}')

            bot.edit_message_text(chat_id=chat_id,
                                  text=text.ANSWER_PHONE,
                                  message_id=message_id,
                                  parse_mode='Markdown',
                                  )

        elif subject == 'location':
            db_functions.update_user_field(user_id, 'input_data', f'location_{booking_id}')

            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass

            bot.send_message(chat_id=chat_id,
                             text=text.ASK_LOCATION,
                             reply_markup=keyboards.location_keyboard(),
                             parse_mode='Markdown',
                             )

    elif query == 'delete':
        area = call_data[1]
        booking_id = int(call_data[2])

        if area == 'booking':
            booking_status = db_functions.get_booking_field(booking_id, 'status')

            if booking_status in ['created', 'waiting_payment']:
                db_functions.update_booking_field(booking_id, 'status', 'canceled')

                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.BOOKING_DELETED,
                                    parse_mode='Markdown',
                                    )
            else:
                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.OUTDATED,
                                    parse_mode='Markdown',
                                    )
        
        elif area == 'payment':
            if db_functions.get_booking_field(booking_id, 'status') == 'waiting_confirm':
                db_functions.update_booking_field(booking_id, 'status', 'canceled')

                try:
                    bot.edit_message_reply_markup(chat_id=chat_id,
                                                  message_id=message_id,
                                                  reply_markup=telebot.types.InlineKeyboardMarkup(),
                                                  )
                except:
                    pass


                bot.send_message(chat_id=chat_id,
                                 text=text.ADMIN_PAYMENT_DECLINED,
                                 parse_mode='Markdown',
                                 reply_to_message_id=message_id,
                                 )

                booking_info = db_functions.get_booking_info(booking_id)
                client_id = booking_info[0]

                bot.send_message(chat_id=client_id,
                                 text=text.booking_declined(booking_id, *booking_info),
                                 parse_mode='Markdown',
                                 disable_notification=False,
                                 )

            else:
                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.OUTDATED,
                                    parse_mode='Markdown',
                                    )
    
    elif query == 'confirm':
        area = call_data[1]
        booking_id = int(call_data[2])

        if area == 'booking':
            if db_functions.get_booking_field(booking_id, 'status') == 'created':
                db_functions.update_booking_field(booking_id, 'status', 'waiting_payment')

                booking_info = db_functions.get_booking_info(booking_id)
                status = booking_info[13]

                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.booking_info(booking_id, *booking_info),
                                    parse_mode='Markdown',
                                    )
                
                bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=keyboards.existing_booking_keyboard(status, booking_id),
                                            )
            
            else:
                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.OUTDATED,
                                    parse_mode='Markdown',
                                    )
        
        elif area == 'payment':
            if db_functions.get_booking_field(booking_id, 'status') == 'waiting_confirm':
                db_functions.update_booking_field(booking_id, 'status', 'awaiting')

                try:
                    bot.edit_message_reply_markup(chat_id=chat_id,
                                                  message_id=message_id,
                                                  reply_markup=telebot.types.InlineKeyboardMarkup(),
                                                  )
                except:
                    pass

                booking_info = db_functions.get_booking_info(booking_id)

                names = eval(booking_info[5])
                passport_photos = eval(booking_info[6])
                stamp_photos = eval(booking_info[7])

                inform_message = bot.send_message(chat_id=chat_id,
                                                text=text.booking_admin_info(booking_id, *booking_info),
                                                parse_mode='Markdown',
                                                reply_to_message_id=message_id,
                                                )

                for index in range(len(names)):
                    group_media = [telebot.types.InputMediaPhoto(passport_photos[index]), telebot.types.InputMediaPhoto(stamp_photos[index])]

                    bot.send_media_group(chat_id=chat_id,
                                        media=group_media,
                                        timeout=30,
                                        reply_to_message_id=inform_message.id,
                                        )
                
                client_id = booking_info[0]

                bot.send_message(chat_id=client_id,
                                 text=text.booking_confirmed(*booking_info),
                                 parse_mode='Markdown',
                                 disable_notification=False,
                                 )

            else:
                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.OUTDATED,
                                    parse_mode='Markdown',
                                    )
    
    elif query == 'paid':
        booking_id = int(call_data[1])

        if db_functions.get_booking_field(booking_id, 'status') == 'waiting_payment':
            db_functions.update_user_field(user_id, 'input_data', f'payment_{booking_id}')

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.ASK_SLIP + text.CANCEL_COMMAND,
                                  parse_mode='Markdown',
                                  )

        else:
            bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=text.OUTDATED,
                                parse_mode='Markdown',
                                )

    elif query == 'close':
        bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=text.CLOSED,
                                parse_mode='Markdown',
                                )

    elif query == 'bus':
        try:
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=telebot.types.InlineKeyboardMarkup(),
                                          )
        except:
            pass
            
        #TODO:
        bot.send_media_group(chat_id=chat_id,
                             media=config.BUSES,
                             )


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Handles message with text type."""

    user_id = message.from_user.id
    chat_id = message.chat.id

    user_info = db_functions.get_info(user_id)
    input_data = db_functions.get_user_field_info(user_id, 'input_data')
    
    is_busy = user_info[1]

    if str(user_id) in config.MANAGER_ID and '#рассылка' in message.text:
        message_to_send = message.text.replace('#рассылка', '')

        threading.Thread(daemon=True, 
                         target=functions.send_marketing_message, 
                         args=(message_to_send, 'text'),
                         ).start()

    elif message.text == '🗓 Забронировать бордер-ран':
        created_booking_id =  db_functions.get_created_booking_id(user_id)
        waiting_payment_booking_id = db_functions.get_waiting_payment_booking_id(user_id)
        waiting_confirm_booking_id = db_functions.get_waiting_confirm_booking_id(user_id)
        awaiting_booking_id = db_functions.get_awaiting_booking_id(user_id)
 
        if waiting_payment_booking_id or waiting_confirm_booking_id or awaiting_booking_id:
            if waiting_payment_booking_id:
                booking_id = waiting_payment_booking_id
            elif waiting_confirm_booking_id:
                booking_id = waiting_confirm_booking_id
            elif awaiting_booking_id:
                booking_id = awaiting_booking_id
            
            booking_info = db_functions.get_booking_info(booking_id)

            status = booking_info[13]
            bot.send_message(chat_id=chat_id,
                             text=text.booking_info(booking_id, *booking_info),
                             reply_markup=keyboards.existing_booking_keyboard(status, booking_id),
                             parse_mode='Markdown',
                             )

        elif created_booking_id:
            booking_info = db_functions.get_booking_info(created_booking_id)

            names = eval(booking_info[5])
            passport_photos = eval(booking_info[6])
            stamp_photos = eval(booking_info[7])

            for index in range(len(names)):
                group_media = [telebot.types.InputMediaPhoto(passport_photos[index]), telebot.types.InputMediaPhoto(stamp_photos[index])]

                bot.send_media_group(chat_id=chat_id,
                                    media=group_media,
                                    timeout=30,
                                    )

            bot.send_message(chat_id=chat_id,
                            text=text.booking_info(created_booking_id, *booking_info),
                            reply_markup=keyboards.change_keyboard(created_booking_id),
                            parse_mode='Markdown',
                            )

        else:
            creating_booking_id = db_functions.get_creating_booking_id(user_id)

            if creating_booking_id:
                db_functions.delete_booking(creating_booking_id)
            
            db_functions.add_booking(user_id, message.from_user.username)
            booking_id = db_functions.get_creating_booking_id(user_id)

            bot.send_message(chat_id=chat_id,
                             text=text.ANSWER_ROUTE,
                             reply_markup=keyboards.route_keyboard(booking_id),
                             parse_mode='Markdown',
                             )
    
    elif message.text == '📝 Мои бронирования':
        created_booking_id =  db_functions.get_created_booking_id(user_id)
        waiting_payment_booking_id = db_functions.get_waiting_payment_booking_id(user_id)
        waiting_confirm_booking_id = db_functions.get_waiting_confirm_booking_id(user_id)
        awaiting_booking_id = db_functions.get_awaiting_booking_id(user_id)
 
        if waiting_payment_booking_id or waiting_confirm_booking_id or awaiting_booking_id:
            if waiting_payment_booking_id:
                booking_id = waiting_payment_booking_id
            elif waiting_confirm_booking_id:
                booking_id = waiting_confirm_booking_id
            elif awaiting_booking_id:
                booking_id = awaiting_booking_id
            
            booking_info = db_functions.get_booking_info(booking_id)

            status = booking_info[13]
            bot.send_message(chat_id=chat_id,
                             text=text.booking_info(booking_id, *booking_info),
                             reply_markup=keyboards.existing_booking_keyboard(status, booking_id),
                             parse_mode='Markdown',
                             )

        elif created_booking_id:
            booking_info = db_functions.get_booking_info(created_booking_id)

            names = eval(booking_info[5])
            passport_photos = eval(booking_info[6])
            stamp_photos = eval(booking_info[7])

            for index in range(len(names)):
                group_media = [telebot.types.InputMediaPhoto(passport_photos[index]), telebot.types.InputMediaPhoto(stamp_photos[index])]

                bot.send_media_group(chat_id=chat_id,
                                    media=group_media,
                                    timeout=30,
                                    )

            bot.send_message(chat_id=chat_id,
                            text=text.booking_info(created_booking_id, *booking_info),
                            reply_markup=keyboards.change_keyboard(created_booking_id),
                            parse_mode='Markdown',
                            )

        else:
            bot.send_message(chat_id=chat_id,
                            text=text.NO_ACTIVE_BOOKINGS,
                            reply_markup=keyboards.book_keyboard(),
                            parse_mode='Markdown',
                            )

    elif message.text == '❓ Помощь':
        bot.send_message(chat_id=chat_id,
                         text=text.HELP_MESSAGE,
                         reply_markup=keyboards.help_keyboard(),
                         parse_mode='Markdown',
                         )

    elif message.text == '🔍 Справка':
        bot.send_message(chat_id=chat_id,
                         text=text.INFO,
                         reply_markup=keyboards.buses_keyboard(),
                         parse_mode='Markdown',
                         )

    elif input_data:
        if 'name' in input_data:
            booking_id = int(input_data.split('_')[-1])
            
            booking_status = db_functions.get_booking_field(booking_id, 'status')
            names = eval(db_functions.get_booking_field(booking_id, 'names'))
            names.append(message.text)

            db_functions.update_booking_field(booking_id, 'names', str(names))

            count = db_functions.get_booking_field(booking_id, 'count')

            if len(names) == count:
                if booking_status and booking_status == 'creating':
                    db_functions.update_user_field(user_id, 'input_data', f'passport_photos_{booking_id}')
                    
                    alone = False
                    if count == 1:
                        alone = True

                    bot.send_message(chat_id=chat_id,
                                 text=text.ask_passport_photos(alone, names[0]),
                                 parse_mode='Markdown',
                                 )

                elif booking_status and booking_status == 'created':
                    db_functions.update_user_field(user_id, 'input_data', None)
                    
                    booking_info = db_functions.get_booking_info(booking_id)

                    names = eval(booking_info[5])
                    passport_photos = eval(booking_info[6])
                    stamp_photos = eval(booking_info[7])

                    for index in range(len(names)):
                        group_media = [telebot.types.InputMediaPhoto(passport_photos[index]), telebot.types.InputMediaPhoto(stamp_photos[index])]

                        bot.send_media_group(chat_id=chat_id,
                                            media=group_media,
                                            timeout=30,
                                            )

                    bot.send_message(chat_id=chat_id,
                                    text=text.booking_info(booking_id, *booking_info),
                                    reply_markup=keyboards.change_keyboard(booking_id),
                                    parse_mode='Markdown',
                                    )
            else:
                bot.send_message(chat_id=chat_id,
                                 text=text.ask_name(False, len(names)),
                                 parse_mode='Markdown',
                                 )
        
        elif 'phone' in input_data:
            booking_id = int(input_data.split('_')[-1])
            if message.text != '-':
                phone = utils.validate_phone(message.text)
            else:
                phone = '-'

            if phone:
                booking_status = db_functions.get_booking_field(booking_id, 'status')
                db_functions.update_booking_field(booking_id, 'phone', phone)

                if booking_status and booking_status == 'creating':
                    db_functions.update_user_field(user_id, 'input_data', f'location_{booking_id}') 

                    bot.send_message(chat_id=chat_id,
                                     text=text.ASK_LOCATION,
                                     reply_markup=keyboards.location_keyboard(),
                                     parse_mode='Markdown',
                                     )

                elif booking_status and booking_status == 'created':
                    db_functions.update_user_field(user_id, 'input_data', None) 
                    
                    booking_info = db_functions.get_booking_info(booking_id)

                    names = eval(booking_info[5])
                    passport_photos = eval(booking_info[6])
                    stamp_photos = eval(booking_info[7])

                    for index in range(len(names)):
                        group_media = [telebot.types.InputMediaPhoto(passport_photos[index]), telebot.types.InputMediaPhoto(stamp_photos[index])]

                        bot.send_media_group(chat_id=chat_id,
                                            media=group_media,
                                            timeout=30,
                                            )

                    bot.send_message(chat_id=chat_id,
                                    text=text.booking_info(booking_id, *booking_info),
                                    reply_markup=keyboards.change_keyboard(booking_id),
                                    parse_mode='Markdown',
                                    )

            else:
                bot.send_message(chat_id=chat_id,
                                 text=text.WRONG_PHONE_FORMAT,
                                 parse_mode='Markdown',
                                 )

    else:
        if is_busy:
            try:
                bot.delete_message(chat_id=chat_id, message_id=message.id)
            except:
                pass

        else:
            db_functions.set_busy(user_id, True)

            history = eval(user_info[0])

            reply_message = bot.send_message(chat_id=chat_id,
                                                text=text.AWAIT,
                                                )
            
            db_functions.update_message_id(user_id, reply_message.id)

            threading.Thread(daemon=True, 
                            target=functions.connect_ai, 
                            args=(reply_message.id,
                                    message.text,
                                    message.id,
                                    history,
                                    user_id,
                                    ),
                            ).start()


@bot.message_handler(content_types=['photo'])
def handle_text(message):
    """Handles message with text type."""

    user_id = message.from_user.id
    chat_id = message.chat.id

    input_data = db_functions.get_user_field_info(user_id, 'input_data')

    photo = message.photo[-1].file_id

    print(photo)
    if str(user_id) in config.MANAGER_ID and message.caption and '#рассылка' in message.caption:
        message_to_send = message.caption.replace('#рассылка', '')

        threading.Thread(daemon=True, 
                         target=functions.send_marketing_message, 
                         args=(message_to_send, 'photo', photo),
                         ).start()

    elif input_data and 'passport_photos' in input_data:
        booking_id = int(input_data.split('_')[-1])
            
        booking_status = db_functions.get_booking_field(booking_id, 'status')
        passport_photos = eval(db_functions.get_booking_field(booking_id, 'passport_photos'))
        names = eval(db_functions.get_booking_field(booking_id, 'names'))
        passport_photos.append(photo)

        db_functions.update_booking_field(booking_id, 'passport_photos', str(passport_photos))

        count = db_functions.get_booking_field(booking_id, 'count')

        current_count = len(passport_photos)
        if current_count == count:
            if booking_status and booking_status == 'creating':
                db_functions.update_user_field(user_id, 'input_data', f'stamp_photos_{booking_id}')
                
                alone = False
                if count == 1:
                    alone = True

                bot.send_message(chat_id=chat_id,
                                text=text.ask_stamp_photos(alone, names[0]),
                                parse_mode='Markdown',
                                )

            elif booking_status and booking_status == 'created':
                db_functions.update_user_field(user_id, 'input_data', None)
                
                booking_info = db_functions.get_booking_info(booking_id)

                names = eval(booking_info[5])
                passport_photos = eval(booking_info[6])
                stamp_photos = eval(booking_info[7])

                for index in range(len(names)):
                    group_media = [telebot.types.InputMediaPhoto(passport_photos[index]), telebot.types.InputMediaPhoto(stamp_photos[index])]

                    bot.send_media_group(chat_id=chat_id,
                                        media=group_media,
                                        timeout=30,
                                        )

                bot.send_message(chat_id=chat_id,
                                text=text.booking_info(booking_id, *booking_info),
                                reply_markup=keyboards.change_keyboard(booking_id),
                                parse_mode='Markdown',
                                )

        else:
            bot.send_message(chat_id=chat_id,
                                text=text.ask_passport_photos(False, names[current_count]),
                                parse_mode='Markdown',
                                )
    
    elif input_data and 'stamp_photos' in input_data:
        booking_id = int(input_data.split('_')[-1])
            
        booking_status = db_functions.get_booking_field(booking_id, 'status')
        stamp_photos = eval(db_functions.get_booking_field(booking_id, 'stamp_photos'))
        names = eval(db_functions.get_booking_field(booking_id, 'names'))
        stamp_photos.append(photo)

        db_functions.update_booking_field(booking_id, 'stamp_photos', str(stamp_photos))

        count = db_functions.get_booking_field(booking_id, 'count')

        current_count = len(stamp_photos)
        if current_count == count:
            if booking_status and booking_status == 'creating':
                db_functions.update_user_field(user_id, 'input_data', f'phone_{booking_id}')

                bot.send_message(chat_id=chat_id,
                                text=text.ANSWER_PHONE,
                                parse_mode='Markdown',
                                )

            elif booking_status and booking_status == 'created':
                db_functions.update_user_field(user_id, 'input_data', None)
                
                booking_info = db_functions.get_booking_info(booking_id)

                names = eval(booking_info[5])
                passport_photos = eval(booking_info[6])
                stamp_photos = eval(booking_info[7])

                for index in range(len(names)):
                    group_media = [telebot.types.InputMediaPhoto(passport_photos[index]), telebot.types.InputMediaPhoto(stamp_photos[index])]

                    bot.send_media_group(chat_id=chat_id,
                                        media=group_media,
                                        timeout=30,
                                        )

                bot.send_message(chat_id=chat_id,
                                text=text.booking_info(booking_id, *booking_info),
                                reply_markup=keyboards.change_keyboard(booking_id),
                                parse_mode='Markdown',
                                )

        else:
            bot.send_message(chat_id=chat_id,
                                text=text.ask_stamp_photos(False, names[current_count]),
                                parse_mode='Markdown',
                                )
    
    elif input_data and 'payment' in input_data:
        booking_id = int(input_data.split('_')[-1])
            
        booking_status = db_functions.get_booking_field(booking_id, 'status')

        if booking_status and booking_status == 'waiting_payment':
            db_functions.update_user_field(user_id, 'input_data', None)
            db_functions.update_booking_field(booking_id, 'status', 'waiting_confirm')

            bot.send_message(chat_id=chat_id,
                             text=text.SLIP_SENDED,
                             parse_mode='Markdown',
                             )

            booking_info = db_functions.get_booking_info(booking_id)

            bot.send_photo(chat_id=config.MANAGER_ID,
                           photo=photo,
                           caption=text.admin_confirm_payment(booking_id, *booking_info),
                           reply_markup=keyboards.confirm_payment_keyboard(booking_id),
                           parse_mode='Markdown',
                           disable_notification=False,
                           )


@bot.message_handler(content_types=['location'])
def handle_contact(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    input_data = db_functions.get_user_field_info(user_id, 'input_data')

    if input_data and 'location' in input_data:
        booking_id = int(input_data.split('_')[-1])

        lat = message.location.latitude
        lon = message.location.longitude
        
        db_functions.update_booking_field(booking_id, 'lat', lat)
        db_functions.update_booking_field(booking_id, 'lon', lon)
        db_functions.update_booking_field(booking_id, 'status', 'created')

        db_functions.update_user_field(user_id, 'input_data', None)

        route = db_functions.get_booking_field(booking_id, 'route')
        count = db_functions.get_booking_field(booking_id, 'count')

        amount_rub = round(config.PRICES[route]['RUB'] * functions.get_exchange_rate() * count, 2)
        amount_thb = config.PRICES[route]['THB'] * count

        db_functions.update_booking_field(booking_id, 'amount_rub', amount_rub)
        db_functions.update_booking_field(booking_id, 'amount_thb', amount_thb)
        
        booking_info = db_functions.get_booking_info(booking_id)

        names = eval(booking_info[5])
        passport_photos = eval(booking_info[6])
        stamp_photos = eval(booking_info[7])

        bot.send_message(chat_id=chat_id,
                         text=text.LOCATION_APPROVED,
                         reply_markup=keyboards.book_keyboard(),
                         parse_mode='Markdown',
                         )

        for index in range(len(names)):
            group_media = [telebot.types.InputMediaPhoto(passport_photos[index]), telebot.types.InputMediaPhoto(stamp_photos[index])]

            bot.send_media_group(chat_id=chat_id,
                                 media=group_media,
                                 timeout=30,
                                 )

        bot.send_message(chat_id=chat_id,
                         text=text.booking_info(booking_id, *booking_info),
                         reply_markup=keyboards.change_keyboard(booking_id),
                         parse_mode='Markdown',
                         )

    
@bot.message_handler(content_types=['video'])
def handle_text(message):
    """Handles message with type text."""

    user_id = str(message.from_user.id)

    if user_id in config.MANAGER_ID and message.caption and'#рассылка' in message.caption:
        message_to_send = message.caption.replace('#рассылка', '')
        video = message.video.file_id

        threading.Thread(daemon=True, 
                         target=functions.send_marketing_message, 
                         args=(message_to_send, 'video', video),
                         ).start()


if __name__ == '__main__':
    # bot.polling(timeout=80)
    while True:
        try:
            bot.polling()
        except:
            pass