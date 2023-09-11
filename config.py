import os
import telebot

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
BOT_ID = os.getenv('BOT_ID')
MANAGER_ID = os.getenv('MANAGER_ID')
MANAGER_USERNAME = os.getenv('MANAGER_USERNAME')

AI_TOKEN = os.getenv('AI_TOKEN')
AI_ENDPOINT = os.getenv('AI_ENDPOINT')

SPREAD_NAME = os.getenv('SPREAD_NAME')
LIST_NAME = os.getenv('LIST_NAME')

BANK = 'Тинькофф'
ACCOUNT = '2200 7006 0230 1037'
NUMBER = '+7 903 202-70-77'
RECEIVER = 'Денис Ш.'

HEADERS = {
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'origin' : 'https://www.bybit.com',
}

# binance url for requests
URL_BYBIT= 'https://api2.bybit.com/fiat/otc/item/online'

# minimal orders count for bybit p2p
ORDERS = 10

# minimal orders rate for bybit p2p
ORDERS_RATE = 0.95

LAST_HOUR = 18

COEFF = 1.025

DAYS_FROM = 25

PRICES = {
    'mal' : {'RUB' : 3500, 'THB' : 3800,},
    'cam' : {'RUB' : 2900, 'THB' : 2900,},
}

BOOKING_STATUSES = {
    'creating' : 'создается',
    'created' : 'ожидает подтверждения данных',
    'waiting_payment' : 'ожидается платеж',
    'waiting_confirm' : 'ожидается подтверждение платежа',
    'awaiting' : 'забронировано, ожидается бордер-ран',
    'finished' : 'выполнено',
    'canceled' : 'отменено',
}

ROUTES = {
    'cam' : 'Паттайя - Камбоджа',
    'mal' : 'Пхукет - Малайзия',
}

COUNT = {
    0 : 'первого',
    1 : 'второго',
    2 : 'третьего',
    3 : 'четвертого',
    4 : 'пятого',
    5 : 'шестого',
    6 : 'седьмого',
    7 : 'восьмого',
    8 : 'девятого',
    9 : 'десятого',
}

BUSES = [
    telebot.types.InputMediaPhoto('AgACAgUAAxkBAAMDZP6QtialfgAB9wNPo6UDLaWN-_JuAAIytTEbR7fRVx-3OgUby377AQADAgADeAADMAQ'),
    telebot.types.InputMediaPhoto('AgACAgUAAxkBAAMFZP6QtlcPfE9mATLT8psrdwWiF0EAAjS1MRtHt9FXi7LwIbM5WRIBAAMCAAN4AAMwBA'),
    telebot.types.InputMediaPhoto('AgACAgUAAxkBAAMGZP6QtjWdPigf36KwFBnwh176BusAAjW1MRtHt9FXcDY8MoFmG8gBAAMCAAN4AAMwBA'),
    telebot.types.InputMediaPhoto('AgACAgUAAxkBAAMEZP6Qth6a-97TpVWh303HmKstmLcAAjO1MRtHt9FXk3cqjWZLLucBAAMCAAN4AAMwBA'),
]



