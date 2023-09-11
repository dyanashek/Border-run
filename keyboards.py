import datetime
import calendar

from telebot import types

import config


def book_keyboard():
    """Keyboard that allows ask for a call."""

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('🗓 Забронировать бордер-ран'))
    keyboard.add(types.KeyboardButton('📝 Мои бронирования'))
    keyboard.add(types.KeyboardButton('🔍 Справка'), types.KeyboardButton('❓ Помощь'))

    return keyboard


def existing_booking_keyboard(status, booking_id):
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.InlineKeyboardMarkup()
    if status == 'waiting_payment':
        keyboard.add(types.InlineKeyboardButton('💵 Оплачено', callback_data = f'paid_{booking_id}'))
        keyboard.add(types.InlineKeyboardButton('❌ Отменить бронирование', callback_data = f'delete_booking_{booking_id}'))

    return keyboard


def count_keyboard(booking_id):
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.InlineKeyboardMarkup(row_width=5)
    
    buttons = []
    for num in range(1, 11):
        buttons.append(types.InlineKeyboardButton(num, callback_data = f'count_{booking_id}_{num}'))

        if num % 5 == 0:
            keyboard.add(*buttons)
            buttons = []

    return keyboard


def route_keyboard(booking_id):
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton('📍 Паттайя - Камбоджа', callback_data = f'route_{booking_id}_cam'))
    keyboard.add(types.InlineKeyboardButton('🌎 Пхукет - Малайзия', callback_data = f'route_{booking_id}_mal'))

    return keyboard


def current_month_keyboard(route, booking_id):
    keyboard = types.InlineKeyboardMarkup(row_width=7)

    current_date = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%d %B %Y")
    keyboard.add(types.InlineKeyboardButton(current_date, callback_data = f'today'))

    week_day_buttons = []
    for week_day in ('Пн.', 'Вт.', 'Ср.', 'Чт.', 'Пт.', 'Сб.', 'Вс.',):
        week_day_buttons.append(types.InlineKeyboardButton(week_day, callback_data = f'nothing'))

    keyboard.add(*week_day_buttons)

    curr_year = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).year
    curr_month = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).month
    curr_day = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).day
    curr_hour = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).hour

    date_buttons = []
    for num, i in enumerate(calendar.Calendar().itermonthdates(year=curr_year, month=curr_month)):
        if i.month != curr_month:
            date_buttons.append(types.InlineKeyboardButton('...', callback_data = f'nothing'))
        else:
            date_day = i.day
            week_day = i.weekday()
            if date_day > curr_day + 1:
                if route == 'cam' or (route == 'mal' and week_day in (0, 2, 4, 6)):
                    date_buttons.append(types.InlineKeyboardButton(i.strftime("%d"), callback_data = f'date_{route}_{curr_year}_{curr_month}_{date_day}_{booking_id}'))
                else:
                    date_buttons.append(types.InlineKeyboardButton('❌', callback_data = f'not-available'))

            elif date_day == curr_day + 1:
                if curr_hour >= config.LAST_HOUR - 1:
                    date_buttons.append(types.InlineKeyboardButton('❌', callback_data = f'not-available'))
                else:
                    if route == 'cam' or (route == 'mal' and week_day in (0, 2, 4, 6)):
                        date_buttons.append(types.InlineKeyboardButton(i.strftime("%d"), callback_data = f'date_{route}_{curr_year}_{curr_month}_{date_day}_{booking_id}'))
                    else:
                        date_buttons.append(types.InlineKeyboardButton('❌', callback_data = f'not-available'))

            else:
                date_buttons.append(types.InlineKeyboardButton('❌', callback_data = f'not-available'))

        if (num + 1) % 7 == 0:
            keyboard.add(*date_buttons)
            date_buttons = []
    
    next_month = curr_month + 1
    next_year = curr_year
    if next_month > 12:
        next_month -= 12
        next_year += 1
    
    next_month_text = datetime.date(year=next_year, month=next_month, day=1).strftime("%B")

    keyboard.add(types.InlineKeyboardButton(f'{next_month_text} »', callback_data = f'next_{next_year}_{next_month}_{route}_{booking_id}'))

    return keyboard


def next_month_keyboard(year, month, route, booking_id):
    keyboard = types.InlineKeyboardMarkup(row_width=7)

    current_date = datetime.date(year=year, month=month, day=1).strftime("%B")
    keyboard.add(types.InlineKeyboardButton(current_date, callback_data = f'today'))

    week_day_buttons = []
    for week_day in ('Пн.', 'Вт.', 'Ср.', 'Чт.', 'Пт.', 'Сб.', 'Вс.',):
        week_day_buttons.append(types.InlineKeyboardButton(week_day, callback_data = f'nothing'))

    keyboard.add(*week_day_buttons)

    curr_hour = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).hour
    curr_day = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).day
    last_month_day = (datetime.date(year=year, month=month, day=1) - datetime.timedelta(days=1)).day

    date_buttons = []
    for num, i in enumerate(calendar.Calendar().itermonthdates(year=year, month=month)):
        if i.month != month:
            date_buttons.append(types.InlineKeyboardButton('...', callback_data = f'nothing'))
        else:
            date_day = i.day
            week_day = i.weekday()

            if date_day == 1 and curr_day == last_month_day and curr_hour >= config.LAST_HOUR - 1:
                date_buttons.append(types.InlineKeyboardButton('❌', callback_data = f'not-available'))
            else:
                if route == 'cam' or (route == 'mal' and week_day in (0, 2, 4, 6)):
                    date_buttons.append(types.InlineKeyboardButton(i.strftime("%d"), callback_data = f'date_{route}_{year}_{month}_{date_day}_{booking_id}'))
                else:
                    date_buttons.append(types.InlineKeyboardButton('❌', callback_data = f'not-available'))
                
        if (num + 1) % 7 == 0:
            keyboard.add(*date_buttons)
            date_buttons = []
    
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
    
    prev_month_text = datetime.date(year=prev_year, month=prev_month, day=1).strftime("%B")

    keyboard.add(types.InlineKeyboardButton(f'« {prev_month_text}', callback_data = f'prev_{route}_{booking_id}'))

    return keyboard


def location_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,)
    keyboard.add(types.KeyboardButton(text = '📍 Отправить локацию', request_location=True,))

    return keyboard


def change_keyboard(booking_id):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton('✅ Подтвердить информацию', callback_data = f'confirm_booking_{booking_id}'))
    keyboard.add(types.InlineKeyboardButton('🗓 Изменить дату', callback_data = f'change_date_{booking_id}'))
    keyboard.add(types.InlineKeyboardButton('🗂 Изменить имена', callback_data = f'change_name_{booking_id}'))
    keyboard.add(types.InlineKeyboardButton('🛂 Изменить фото паспортов', callback_data = f'change_passport_{booking_id}'))
    keyboard.add(types.InlineKeyboardButton('🔍 Изменить фото штампов', callback_data = f'change_stamp_{booking_id}'))
    keyboard.add(types.InlineKeyboardButton('📱 Изменить телефон', callback_data = f'change_phone_{booking_id}'))
    keyboard.add(types.InlineKeyboardButton('📍 Изменить локацию', callback_data = f'change_location_{booking_id}'))
    keyboard.add(types.InlineKeyboardButton('❌ Отменить бронирование', callback_data = f'delete_booking_{booking_id}'))
    
    return keyboard


def confirm_payment_keyboard(booking_id):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton('✅ Платеж получен', callback_data = f'confirm_payment_{booking_id}'))
    keyboard.add(types.InlineKeyboardButton('❌ Неверный перевод', callback_data = f'delete_payment_{booking_id}'))
    
    return keyboard


def help_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton('💬 Связаться с администратором', url = f'https://t.me/{config.MANAGER_USERNAME}'))
    keyboard.add(types.InlineKeyboardButton('❌ Закрыть', callback_data = f'close'))

    return keyboard


def buses_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton('🚐 Фото автобусов', callback_data = f'bus'))

    return keyboard