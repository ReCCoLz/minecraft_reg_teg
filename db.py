import sqlite3


conn = sqlite3.connect('users_mine.db')
cur = conn.cursor()


def add_log(login, pwd, id):
    cur.execute('INSERT INTO players VALUES (?, ?, ?, ?);', (login, pwd, id, 0))
    conn.commit()


def get_logins():
    return list(map(lambda x: x[0], cur.execute('SELECT login FROM players').fetchall()))


def get_pass():
    return list(map(lambda x: x[0], cur.execute('SELECT pwd FROM players').fetchall()))


def get_id():
    return list(map(lambda x: x[0], cur.execute('SELECT id FROM players').fetchall()))


def get_all():
    return cur.execute('SELECT * FROM players').fetchall()


def login(login, pwd):
    temp = cur.execute('SELECT * FROM players WHERE login = ? AND pwd = ?', (login, pwd)).fetchone()
    if temp != None and login in temp[0] and str(pwd) in temp[1]:
        cur.execute('UPDATE players SET status = ? WHERE login = ?', (1, login))
        conn.commit()
        return True
    else:
        return False


def logout(login, pwd):
    temp = cur.execute('SELECT * FROM players WHERE login = ? AND pwd = ?', (login, pwd)).fetchone()
    if temp != None and login in temp[0] and str(pwd) in temp[1]:
        cur.execute('UPDATE players SET status = ? WHERE login = ?', (0, login))
        conn.commit()
        return True
    else:
        return False


def check_auth(login):
    status = cur.execute('SELECT status FROM players WHERE login = ?', (login, )).fetchone()
    if status != None and status[0] == 1:
        return True
    else:
        return False
