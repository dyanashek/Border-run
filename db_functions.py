import sqlite3
import logging
import inspect
import datetime
import itertools

import config

def is_in_database(user_id):
    """Checks if user already in database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    users = cursor.execute(f'''SELECT COUNT(id) 
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return users


def add_user(user_id, user_username):
    """Adds a new user to database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''
        INSERT INTO users (user_id, username, history)
        VALUES (?, ?, ?)
        ''', (user_id, user_username, "[]",))
        
    database.commit()
    cursor.close()
    database.close()


def get_message_id(user_id):
    """Gets user's information."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    message_id = cursor.execute(f'''SELECT message_id
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()
    
    cursor.close()
    database.close()

    if message_id:
        message_id = message_id[0][0]

    return message_id


def update_message_id(user_id, message_id):
    '''Updates message's id.'''

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''UPDATE users
                    SET message_id=?
                    WHERE user_id=?
                    ''', (message_id, user_id,))

    database.commit()
    cursor.close()
    database.close()


def get_info(user_id):
    """Gets user's information."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    info = cursor.execute(f'''SELECT history, busy
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()[0]
    
    cursor.close()
    database.close()

    return info


def update_history(user_id, new_history):
    """Updates counter in database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''UPDATE users
                    SET history=?
                    WHERE user_id=?
                    ''', (new_history, user_id,))

    database.commit()
    cursor.close()
    database.close()


def set_busy(user_id, status):
    """Updates busy status to True."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''UPDATE users
                    SET busy=?
                    WHERE user_id=?
                    ''', (status, user_id,))

    database.commit()
    cursor.close()
    database.close()


def get_user_field_info(user_id, field):
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        info = cursor.execute(f'''SELECT {field}
                                FROM users 
                                WHERE user_id=?
                                ''', (user_id,)).fetchall()[0][0]
        
        cursor.close()
        database.close

        return info
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось получить информацию о поле {field} пользователя ({user_id}). {ex}')


def update_user_field(user_id, field, value):
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        cursor.execute(f'''UPDATE users
                        SET {field}=?
                        WHERE user_id=?
                        ''', (value, user_id,))

        database.commit()
        cursor.close()
        database.close()

        logging.info(f'{inspect.currentframe().f_code.co_name}: Поле ({field}) пользователя {user_id} изменено на {value}.')

    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось изменить поле ({field}) пользователя {user_id} на {value}. {ex}')


def get_all_users_ids():
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        users_ids = cursor.execute('SELECT DISTINCT(user_id) FROM users').fetchall()
        
        cursor.close()
        database.close

        if users_ids:
            users_ids = itertools.chain.from_iterable(users_ids)

        return users_ids
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad. {ex}')

    
#! ДЛЯ РАБОТЫ С БРОНИРОВАНИЕМ
def get_booking_field(booking_id, field):
    try:
        database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = database.cursor()

        info = cursor.execute(f'''SELECT {field}
                                FROM bookings
                                WHERE id=?
                                ''', (booking_id,)).fetchall()[0][0]
        
        cursor.close()
        database.close

        return info
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось получить информацию о поле {field} пользователя ({booking_id}). {ex}')


def update_booking_field(booking_id, field, value):
    try:
        database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = database.cursor()

        cursor.execute(f'''UPDATE bookings
                        SET {field}=?
                        WHERE id=?
                        ''', (value, booking_id,))

        database.commit()
        cursor.close()
        database.close()

        logging.info(f'{inspect.currentframe().f_code.co_name}: Поле ({field}) пользователя {booking_id} изменено на {value}.')

    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось изменить поле ({field}) пользователя {booking_id} на {value}. {ex}')

    
def get_creating_booking_id(user_id):
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        booking_id = cursor.execute(f'''SELECT id
                                FROM bookings
                                WHERE user_id=? AND status=?
                                ''', (user_id, 'creating',)).fetchall()
        
        cursor.close()
        database.close

        if booking_id:
            booking_id = booking_id[0][0]

        return booking_id
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad. {ex}')


def get_created_booking_id(user_id):
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        booking_id = cursor.execute(f'''SELECT id
                                FROM bookings
                                WHERE user_id=? AND status=?
                                ''', (user_id, 'created',)).fetchall()
        
        cursor.close()
        database.close

        if booking_id:
            booking_id = booking_id[0][0]

        return booking_id
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad. {ex}')


def get_waiting_payment_booking_id(user_id):
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        booking_id = cursor.execute(f'''SELECT id
                                FROM bookings
                                WHERE user_id=? AND status=?
                                ''', (user_id, 'waiting_payment',)).fetchall()
        
        cursor.close()
        database.close

        if booking_id:
            booking_id = booking_id[0][0]

        return booking_id
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad. {ex}')


def get_waiting_confirm_booking_id(user_id):
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        booking_id = cursor.execute(f'''SELECT id
                                FROM bookings
                                WHERE user_id=? AND status=?
                                ''', (user_id, 'waiting_confirm',)).fetchall()
        
        cursor.close()
        database.close

        if booking_id:
            booking_id = booking_id[0][0]

        return booking_id
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad. {ex}')


def get_awaiting_booking_id(user_id):
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        booking_id = cursor.execute(f'''SELECT id
                                FROM bookings
                                WHERE user_id=? AND status=?
                                ''', (user_id, 'awaiting',)).fetchall()
        
        cursor.close()
        database.close

        if booking_id:
            booking_id = booking_id[0][0]

        return booking_id
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad. {ex}')


def delete_booking(booking_id):
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        cursor.execute('DELETE FROM bookings WHERE id=?', (booking_id,))
        
        database.commit()
        cursor.close()
        database.close

    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad. {ex}')


def add_booking(user_id, username):
    try:
        database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = database.cursor()

        cursor.execute(f'''
            INSERT INTO bookings (user_id, username, names, passport_photos, stamp_photos, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, '[]', '[]', '[]', 'creating'))
            
        database.commit()
        cursor.close()
        database.close()
        

        logging.info(f'{inspect.currentframe().f_code.co_name}: good.')

    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad. {ex}')


def get_booking_info(booking_id):
    try:
        database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = database.cursor()

        booking_info = cursor.execute(f'''SELECT user_id, username, route, book_date, count, names, passport_photos, stamp_photos, lat, lon, phone, amount_rub, amount_thb, status
                                FROM bookings
                                WHERE id=?
                                ''', (booking_id,)).fetchall()[0]
        
        cursor.close()
        database.close

        return booking_info
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad. {ex}')


def update_finished_status():
    try:
        database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = database.cursor()

        curr_date = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).date()

        cursor.execute(f'''UPDATE bookings
                        SET status=?
                        WHERE book_date<? and status=?
                        ''', ('finished', curr_date, 'awaiting',))
        
        database.commit()
        cursor.close()
        database.close
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad. {ex}')


def select_unpaid():
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        tomorrow = (datetime.datetime.utcnow() + datetime.timedelta(hours=7) + datetime.timedelta(days=1)).date()
        
        bookings_ids = cursor.execute(f'''SELECT id
                                FROM bookings 
                                WHERE book_date=? AND (status=? OR status=?)
                                ''', (tomorrow, 'created', 'waiting_payment',)).fetchall()
        
        cursor.close()
        database.close

        if bookings_ids:
            bookings_ids = itertools.chain.from_iterable(bookings_ids)

        return bookings_ids
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad {ex}')


def get_needed_new_booking():
    try:
        database = sqlite3.connect("db.db")
        cursor = database.cursor()

        date_needed = (datetime.datetime.utcnow() + datetime.timedelta(hours=7) - datetime.timedelta(days=config.DAYS_FROM)).date()
        
        bookings_ids = cursor.execute(f'''SELECT id
                                FROM bookings 
                                WHERE book_date=? AND status=? AND informed=?
                                ''', (date_needed, 'finished', False,)).fetchall()
        
        cursor.close()
        database.close

        if bookings_ids:
            bookings_ids = itertools.chain.from_iterable(bookings_ids)

        return bookings_ids
    
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: bad {ex}')