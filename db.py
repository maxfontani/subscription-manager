import re
import sqlite3
import hashlib
import classes
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

DB_PATH = r'DB\\Main.db'

# CONNECT TO THE DB
def connect_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        return conn,cursor

    except Exception:
        raise Exception('Connection to the DB failed!')


# backup function
def backup_db():
    try:
        today = date.today()
        bk_path = r'DB\backup_' + str(today) + '.db'
        source = sqlite3.connect(DB_PATH)
        backup = sqlite3.connect(bk_path)
        source.backup(backup)

    except Exception as ex:
        print(str(ex))
        raise Exception('DB backup process failed!')


# Connect to the DB, enable FK constrainsts, and create a Cursor object
def create_db(name):
    conn = sqlite3.connect(str(name))
    with conn:
        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS clients (
                    client_ID INTEGER PRIMARY KEY,
                    name text,
                    tel text,
                    email text,
                    level text,
                    last_active_date text
            )""")
        conn.commit()

        cursor.execute("""CREATE TABLE IF NOT EXISTS subscriptions (
                    sub_ID INTEGER PRIMARY KEY,
                    holder integer,
                    date_issued text,
                    date_ends text,
                    sub_type integer,
                    status integer,
                    days_frozen,
                    FOREIGN KEY(holder) REFERENCES clients(client_ID)  
            )""")
        conn.commit()


# add clinet function
def add_client(client, conn, cursor):
    with conn:
        # Telephone number format restrictions: 10-digit without spaces
        pattern = re.compile(r"^\d{10}$")
        check = pattern.fullmatch(client.tel)

        if check is None:
            raise ValueError('WRONG TEL FORMAT!')

        # Check the email format if it was indicated
        if client.email is not None:
            pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
            check = pattern.fullmatch(client.email)

            if check is None:
                raise ValueError('WRONG EMAIL FORMAT!')

        # Check whether the tel number already exists in the DB
        cursor.execute("SELECT tel FROM clients")
        tel_list = [row[0] for row in cursor.fetchall()]
        if client.tel in tel_list:
            raise Exception('TEL NUMBER ALREADY EXISTS IN THE DB!')

        # Check whether the name already exists in the DB
        cursor.execute("SELECT name FROM clients")
        name_list = [row[0] for row in cursor.fetchall()]
        if client.name in name_list:
            raise Exception('THE NAME ALREADY EXISTS IN THE DB!')

        # If the checks passed, add the new client
        cursor.execute("INSERT INTO clients(name, tel, email, level, last_active_date) VALUES (?,?,?,?,?)", (client.name, client.tel, client.email, client.level, client.last_active_date))

# add subscription function
def add_sub(sub, conn, cursor):
    with conn:
        cursor.execute("INSERT INTO subscriptions(holder, date_issued, date_ends, sub_type, status, days_frozen) VALUES (?,?,?,?,?,?)", (sub.holder, sub.date_issued, sub.date_ends, sub.sub_type, sub.status, sub.days_frozen))
        cursor.execute("UPDATE clients SET last_active_date = (?) WHERE client_ID = (?)", (sub.date_ends,sub.holder))

# remove subscription entry from DB
def remove_sub(id, conn, cursor):
    with conn:
        try:
            cursor.execute("DELETE FROM subscriptions WHERE sub_ID = (?)", (id,))
        except Exception as ex:
            raise Exception(f'REMOVE_SUB FAILED: {ex}')

# The function freezes the subscription with the given ID
def freeze_sub(id, days, conn, cursor):
    with conn:
        cursor.execute('UPDATE subscriptions SET days_frozen = days_frozen + (?) WHERE sub_ID = (?)',(days,id))
        current_date_ends = cursor.execute('SELECT date_ends FROM subscriptions WHERE sub_ID = (?)', (id,)).fetchone()[0]
        date_ends_obj = datetime.strptime(current_date_ends, '%d/%m/%Y')
        new_date_ends_obj = date_ends_obj + relativedelta(days=+days)
        new_date_ends = new_date_ends_obj.strftime('%d/%m/%Y')
        cursor.execute('UPDATE subscriptions SET date_ends = (?) WHERE sub_ID = (?)',(new_date_ends,id))

# Updates the subscriptions' statuses if they have expired
# Conditions: 'all' - update both subs of both ACTIVE and ENDED statuses
# 'active' or 'inactive' - update either one
def update_sub_status(condition = 'all'):
    conn, cursor = connect_db()
    with conn:
        today = date.today()
        if condition == 'active' or condition == 'all':
            cursor.execute("SELECT sub_ID, date_ends FROM subscriptions WHERE status = 'ACTIVE'")
            for row, form in enumerate(cursor.fetchall()):
                current_date_ends = datetime.strptime(form[1], '%d/%m/%Y').date()
                if current_date_ends < today:
                    cursor.execute("UPDATE subscriptions SET status = 'ENDED' WHERE sub_ID = (?)", (form[0],))
        if condition == 'inactive' or condition == 'all':
            cursor.execute("SELECT sub_ID, date_ends FROM subscriptions WHERE status = 'ENDED'")
            for row, form in enumerate(cursor.fetchall()):
                current_date_ends = datetime.strptime(form[1], '%d/%m/%Y').date()
                if current_date_ends >= today:
                    cursor.execute("UPDATE subscriptions SET status = 'ACTIVE' WHERE sub_ID = (?)", (form[0],))

# Password hasher function
def hashed(password):
    return hashlib.sha1(password.encode('utf-8')).hexdigest()

if __name__ == "__main__":
    pass

