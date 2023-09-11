import sqlite3

database = sqlite3.connect("db.db")
cursor = database.cursor()

try:
    cursor.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        user_id TEXT,
        username TEXT,
        history TEXT,
        message_id TEXT,
        busy BOOLEAN DEFAULT FALSE,
        input_data TEXT
        )''')

except:
    print('Users table already exists.')

try:
    # creates table with new users and their referrals
    cursor.execute('''CREATE TABLE bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        username TEXT,
        route TEXT,
        book_date DATE,
        count INTEGER,
        names TEXT,
        passport_photos TEXT,
        stamp_photos TEXT,
        lat REAL,
        lon REAL,
        phone TEXT,
        amount_rub REAL,
        amount_thb REAL,
        status TEXT,
        informed BOOLEAN DEFAULT False
        )''')

except:
    print('Booking table already exists.')