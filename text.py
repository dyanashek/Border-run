import datetime

import utils
import config


START_TEXT = '''Здравствуйте, я AI ассистент сервиса X-change.\nЯ отвечу на ваши вопросы о бордер-ране и помогу забронировать дату.'''

HELP_MESSAGE = '''
                \nКоманды:\
                \n/reload - обнуляет историю сообщений;\
                \n/cancel - отменяет обработку запроса;\
                \n/help - вызывает список доступных команд.\
                '''

ERROR_TEXT = 'Что-то пошло не так, повторите попытку позже. Если проблема носит регулярный характер - воспользуйтесь командой */reload* для сброса истории общения с ботом.'

AWAIT = 'Подождите, Ваш запрос обрабатывается...'

CLEAR_HISTORY = 'История сообщений успешно очищена.'

CANCELED_REQUESTS = 'Все запросы к серверу отменены.'

ANSWER_ROUTE = 'Выберите маршрут:'

ANSWER_DATA = 'Выберите удобную дату:'

ANSWER_COUNT = 'Сколько человек поедет на бордер-ран?'

ANSWER_PHONE = 'Введите свой тайский номер телефона.\n\nНапример: *096-0000000* (+66 меняем на 0)\n\nЕсли тайского номера нет укажите прочерк *-*.'

WRONG_PHONE_FORMAT = 'Введен *неверный формат*.\n\nТелефон должен начинаться с 0 (+66 меняем на 0), состоять из 10 цифр.\n*Например:* 096-1234567\n\nЕсли тайского номера нет укажите прочерк *-*.'

ASK_LOCATION = 'Отправьте локацию точки, откуда вас можно забрать.\n\nУкажите локацию своего *отеля/кондо* (*нажмите скрепку* рядом с полем ввода -> выберите *"геопозиция"* или воспользуйтесь кнопкой *"отправить локацию"*, если в данный момент находитесь в нужном месте).'

OUTDATED = 'Данные устарели.'

LOCATION_APPROVED = 'Данные по геолокации приняты.'

BOOKING_DELETED = 'Бронирование *успешно отменено*.'

INPUT_CANCELED = 'Ввод успешно *отменен*.'

ASK_SLIP = 'Отправьте *скриншот*, подтверждающий перевод.'

CANCEL_COMMAND = '\n\nЕсли вы еще не успели совершить перевод - воспользуйтесь командой */cancel_slip*.'

SLIP_SENDED = 'Информация о платеже направлена *администратору*, мы пришлем уведомление, когда *подтвердим платеж*.'

ADMIN_PAYMENT_DECLINED = 'Платеж *не подтвержден*.'

NO_ACTIVE_BOOKINGS = 'У вас нет активных бронирований, воспользуйтесь кнопкой *"забронировать бордер-ран"* для создания брони.'

HELP_MESSAGE = 'Если у вас возникли вопросы, с которыми не может помочь наш *AI-консультант*, свяжите с *администратором*, воспользовавшись кнопкой ниже.'

CLOSED = 'Раздел закрыт.'

NEED_NEW_BORDER = f'С вашего последнего бордер-рана прошло *{config.DAYS_FROM} дней*. Чтоб не превысить допустимое время нахождения в стране - *забронируйте следующий*!'

INFO = '''
        \n1. *Пхукет - Малайзия*\
        \n- Цена составляет 3800 бат\
        \n- Если оплата в рублях - цена 3500 бат (в рублевом эквиваленте)\
        \n- Трансфер осуществляется в пн., ср., пт., вс (4:30 утра)\
        \n- В цену входит гарантия получения штампа, обед, набор снэков и вода в дорогу, трансфер отеля\
        \n- Время возвращения в отель примерно в 21-22 часа вечером того же дня\
        \n\
        \n2. *Паттайя - Камбоджа*\
        \n- Цена 2900 бат\
        \n- Трансфер осуществляется ежедневно (4:30 утра)\
        \n- В цену  входит гарантия прохождения границы, обед, трансфер из отеля.\
        \n- Время возвращения в отель примерно в середине дня\
        \n\
        \n*Примечания:*\
        \n- Примерное время выезда 04:30 утра\
        \n- С собой из документов нужно взять только загранпаспорт\
        \n- Можете захватить кофту, в машине бывает прохладно, ехать 7 часов в одну сторону\
        \n- В поездке будут остановки на заправках, можно размяться, подышать воздухом или зайти в магазин\
        '''

def booking_info(booking_id, user_id, username, route, book_date, count, names, passport_photos, stamp_photos, lat, lon, phone, amount_rub, amount_thb, status):
    route = config.ROUTES[route]
    booking_date = book_date.strftime("%d.%m.%Y")
    names = utils.escape_markdown(', '.join(eval(names)))
    google_maps_link = utils.generate_google_maps_link(lat, lon)
    amount_rub = utils.numbers_format(amount_rub)
    amount_thb = utils.numbers_format(amount_thb)
    status_text = config.BOOKING_STATUSES[status]

    reply_text = f'''
                \n*БРОНИРОВАНИЕ {booking_date}:*\
                \n\
                \n*Маршрут:* {route}\
                \n*Статус:* {status_text}\
                \n*Количество человек:* {count}\
                \n*Имена:* {names}\
                \n*Номер телефона:* {phone}\
                \n*Стоимость в рублях:* {amount_rub} руб.\
                \n*Стоимость в батах:* {amount_thb} THB\
                \n*Забрать от:* [локация]({google_maps_link})\
                '''

    if status == 'waiting_payment':
        payment_date = (book_date - datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        reply_text += f'''
                    \nВам необходимо оплатить бронирование до *{config.LAST_HOUR}:00 {payment_date}*, в противном случае оно будет *отменено автоматически*.\
                    \n\
                    \nРеквизиты для оплаты в RUB *({amount_rub} руб.)*:\
                    \n*Банк:* {config.BANK}\
                    \n*Номер карты:* {config.ACCOUNT}\
                    \n*Номер телефона:* {config.NUMBER}\
                    \n*Получатель:* {config.RECEIVER}\
                    \n\
                    \nРеквизиты для оплаты в THB *({amount_thb} бат)*:\
                    \n*Банк:* BANGKOK BANK\
                    \n*Номер счета:* 504-0-885336\
                    \n*Получатель:* MR DENIS SHELAGINOV\
                    \n\
                    \n*ВАЖНО:* в комментарии к платежу укажите код *{1000 + booking_id}*. Отсутствие кода может привести к отмене бронирования.\
                    \n\
                    \nПосле оплаты, воспользуйтесь кнопкой *"оплачено"* - вам понадобится *предоставить скриншот*, подтверждающий платеж.\
                    '''
    
    elif status == 'created':
        reply_text += f'''
                    \nПроверьте данные своего бронирования, вы можете *внести необходимые изменения* - после подтверждения, это можно будет сделать только *с помощью администратора*.\
                    \n\
                    \nДля изменения *маршрута* или *количества человек* - удалите текущее бронирование и создайте новое.\
                    \n\
                    \nДля подтверждения бронирования воспользуйтесь кнопкой *"подтвердить информацию"*.\
                    '''

    return reply_text


def ask_name(alone, count):
    if alone:
        reply_text = 'Введите имя и фамилию, как в паспорте.\nНапример: *Ivanov Ivan*'
    else:
        reply_text = f'Введите имя и фамилию *{config.COUNT[count]} человека*, как в паспорте.\nНапример: *Ivanov Ivan*.'
    
    return reply_text


def ask_passport_photos(alone, name):
    if alone:
        reply_text = 'Отправьте фотографию *первой страницы* загран. паспорта (разворот).'
    else:
        name = utils.escape_markdown(name)
        reply_text = f'Отправьте фотографию *первой страницы* загран. паспорта (разворот) {name}.'
    
    return reply_text


def ask_stamp_photos(alone, name):
    if alone:
        reply_text = 'Отправьте фотографию *последнего штампа* о пересечении границы Таиланда.'
    else:
        name = utils.escape_markdown(name)
        reply_text = f'Отправьте фотографию *последнего штампа* о пересечении границы Таиланда {name}.'
    
    return reply_text


def admin_confirm_payment(booking_id, user_id, username, route, book_date, count, names, passport_photos, stamp_photos, lat, lon, phone, amount_rub, amount_thb, status):
    amount_rub = utils.numbers_format(amount_rub)
    amount_thb = utils.numbers_format(amount_thb)

    return f'Подтвердите получение платежа на сумму *{amount_rub} руб.* или *{amount_thb} бат* с комментарием *{1000 + booking_id}*.'


def booking_admin_info(booking_id, user_id, username, route, book_date, count, names, passport_photos, stamp_photos, lat, lon, phone, amount_rub, amount_thb, status):
    if username:
        username = f'@{utils.escape_markdown(username)}'
    else:
        username = 'не указано'

    route = config.ROUTES[route]
    booking_date = book_date.strftime("%d.%m.%Y")
    names = utils.escape_markdown(', '.join(eval(names)))
    google_maps_link = utils.generate_google_maps_link(lat, lon)
    amount_rub = utils.numbers_format(amount_rub)
    amount_thb = utils.numbers_format(amount_thb)

    reply_text = f'''
                \n*ПОДТВЕРЖДЕНО БРОНИРОВАНИЕ {booking_date} ({1000 + booking_id}):*\
                \n\
                \n*Пользователь:* {username}\
                \n*Маршрут:* {route}\
                \n*Количество человек:* {count}\
                \n*Имена:* {names}\
                \n*Номер телефона:* {phone}\
                \n*Стоимость в рублях:* {amount_rub} руб.\
                \n*Стоимость в батах:* {amount_thb} THB\
                \n*Локация:* {google_maps_link}\
                '''
    
    return reply_text


def booking_confirmed(user_id, username, route, book_date, count, names, passport_photos, stamp_photos, lat, lon, phone, amount_rub, amount_thb, status):
    route = config.ROUTES[route]
    booking_date = book_date.strftime("%d.%m.%Y")
    names = utils.escape_markdown(', '.join(eval(names)))
    google_maps_link = utils.generate_google_maps_link(lat, lon)
    amount_rub = utils.numbers_format(amount_rub)
    amount_thb = utils.numbers_format(amount_thb)
    status_text = config.BOOKING_STATUSES[status]

    reply_text = f'''
                \n*БРОНИРОВАНИЕ ПОДТВЕРЖДЕНО {booking_date}:*\
                \n\
                \n*Маршрут:* {route}\
                \n*Статус:* {status_text}\
                \n*Количество человек:* {count}\
                \n*Имена:* {names}\
                \n*Номер телефона:* {phone}\
                \n*Стоимость в рублях:* {amount_rub} руб.\
                \n*Стоимость в батах:* {amount_thb} THB\
                \n*Забрать от:* [локация]({google_maps_link})\
                '''
    
    return reply_text


def booking_declined(booking_id, user_id, username, route, book_date, count, names, passport_photos, stamp_photos, lat, lon, phone, amount_rub, amount_thb, status):
    route = config.ROUTES[route]
    booking_date = book_date.strftime("%d.%m.%Y")
    names = utils.escape_markdown(', '.join(eval(names)))
    google_maps_link = utils.generate_google_maps_link(lat, lon)
    amount_rub = utils.numbers_format(amount_rub)
    amount_thb = utils.numbers_format(amount_thb)
    status_text = config.BOOKING_STATUSES[status]

    reply_text = f'''
                \n*Платеж по бронированию не подтвержден {booking_date}:*\
                \n\
                \n*Маршрут:* {route}\
                \n*Статус:* {status_text}\
                \n*Количество человек:* {count}\
                \n*Имена:* {names}\
                \n*Номер телефона:* {phone}\
                \n*Стоимость в рублях:* {amount_rub} руб.\
                \n*Стоимость в батах:* {amount_thb} THB\
                \n*Забрать от:* [локация]({google_maps_link})\
                \n\
                \nМожете воспользоваться кнопкой *помощь* для связи с администратором, идентификатор отмененного бронирования: *{1000 + booking_id}*.\
                '''
    
    return reply_text


def unpaid_booking_declined(booking_id, user_id, username, route, book_date, count, names, passport_photos, stamp_photos, lat, lon, phone, amount_rub, amount_thb, status):
    route = config.ROUTES[route]
    booking_date = book_date.strftime("%d.%m.%Y")
    names = utils.escape_markdown(', '.join(eval(names)))
    google_maps_link = utils.generate_google_maps_link(lat, lon)
    amount_rub = utils.numbers_format(amount_rub)
    amount_thb = utils.numbers_format(amount_thb)
    status_text = config.BOOKING_STATUSES[status]

    reply_text = f'''
                \n*Бронированию отклонено {booking_date}, прошел срок платежа:*\
                \n\
                \n*Маршрут:* {route}\
                \n*Статус:* {status_text}\
                \n*Количество человек:* {count}\
                \n*Имена:* {names}\
                \n*Номер телефона:* {phone}\
                \n*Стоимость в рублях:* {amount_rub} руб.\
                \n*Стоимость в батах:* {amount_thb} THB\
                \n*Забрать от:* [локация]({google_maps_link})\
                \n\
                \nМожете воспользоваться кнопкой *помощь* для связи с администратором, идентификатор отклоненного бронирования: *{1000 + booking_id}*.\
                '''
    
    return reply_text