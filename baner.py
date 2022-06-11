import sqlite3
from mcpi.minecraft import Minecraft
import mcpi.block as block
import time

mc = Minecraft.create()  # todo: подключиться к серверу
conn = sqlite3.connect('users_mine.db')
cur = conn.cursor()

def ban(name):
    mc.postToChat(f'/ban {name}')


def unban(name):
    mc.postToChat(f'/pardon {name}')


def islogin(name):
    return cur.execute(f'SELECT status FROM players WHERE login = {name}')


while True:
    players = []  # todo: каким-то хуем достать список всех онлайн игроков на сервере
    for i in players:
        if islogin(i) is None or islogin(i) == 1:
            ban(i)
        # todo: придумать как разбанивать этих игроков, возможно добавить в бд новый столбец
    time.sleep(5)
