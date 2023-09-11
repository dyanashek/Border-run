import datetime
import sqlite3
import threading
import logging
import itertools

import config


# обновление данных в БД
def update_database_route(route_id, addresses, phones, info_messages, points_num):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    addresses = '*&?#'.join(addresses)
    phones = '*&?#'.join(phones)
    info_messages = '*&?#'.join(info_messages)

    cursor.execute(f'''UPDATE routes
                    SET addresses=?, phones=?, messages=?, route=?
                    WHERE unique_id=?
                    ''', (addresses, phones, info_messages, points_num, route_id,))

    database.commit()
    cursor.close()
    database.close()


# выборка из БД
def get_address_phone(route_id):
    '''Gets address and phone of the point which is next to visit.'''

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    point_info = cursor.execute(f'''SELECT addresses, phones, messages 
                    FROM routes
                    WHERE unique_id=?
                    ''', (route_id,)).fetchall()[0]
    
    cursor.close()
    database.close()

    addresses = point_info[0].split('*&?#')
    phones = point_info[1].split('*&?#')
    info_messages = point_info[2].split('*&?#')

    point_info = tuple(zip(addresses, phones, info_messages))

    return point_info


# база данных с временной меткой
def database_with_timestamp():
    database = sqlite3.connect("china_travel.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = database.cursor()

    try:
        # creates table with information about users
        cursor.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            join_date TIMESTAMP
        )''')
    except Exception as ex:
        logging.error(f'Users table already exists. {ex}')


# google таблицы
# def google_connect():
#     # подключение
#     service_acc = gspread.service_account(filename='service_account.json')
#     sheet = service_acc.open(config.SPREAD_NAME)
#     work_sheet = sheet.worksheet(config.LIST_NAME)

#     # запись данных
#     work_sheet.update('A1:EV1', [[1, 2, 3, 4, 5]])

#     # изменение формата
#     work_sheet.format(f'A1:EV1', {"backgroundColor": {"red": 0.84, "green": 0.68, "blue": 0.0}})

#     # поиск первой пустой строки
#     len(work_sheet.col_values(1)) + 1


# потоки
# threading.Thread(daemon=True, target=google_connect, args=('123',)).start()

# время в строку
current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%d.%m.%Y %H:%M")

# типы контента
content_types = ['text', 'audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker']

# фильтр в бд по времени + развертывание вложенных списков
def select_expired_users():
    database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = database.cursor()

    time_filter = datetime.datetime.utcnow() + datetime.timedelta(hours=3)

    users = cursor.execute(f'''SELECT user_id 
                            FROM users 
                            WHERE subscribe=? and valid_till<?
                            ''', (True, time_filter,)).fetchall()
    
    cursor.close()
    database.close()

    if users:
        users = itertools.chain.from_iterable(users)
    
    return users