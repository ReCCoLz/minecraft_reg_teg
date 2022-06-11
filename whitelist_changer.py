<<<<<<< HEAD
import config 
import db
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InputFile
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import logging


logging.basicConfig(level=logging.INFO)

bot = Bot(config.token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


cancel_but = KeyboardButton('/cancel')
login_but = KeyboardButton('/login')
logout_but = KeyboardButton('/logout')
reg_but = KeyboardButton('/reg')
help_but = KeyboardButton('/help')
get_but = KeyboardButton('/get')

help_kb = ReplyKeyboardMarkup(resize_keyboard=True)
help_kb.add(cancel_but, reg_but, login_but, logout_but, get_but, help_but)

greet_kb =ReplyKeyboardMarkup(resize_keyboard=True)
greet_kb.add(help_but)

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_kb.add(cancel_but)

get_kb = ReplyKeyboardMarkup(resize_keyboard=True)
get_kb.add(get_kb)

class Form(StatesGroup):
    username = State() 
    pwd = State() 


class Login(StatesGroup):
    login = State()
    pwd = State()


class LogOut(StatesGroup):
    login = State()
    pwd = State()


#main handlers

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Привет, раб майнкрафта! Все команды лежат в /help.', reply_markup=greet_kb)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await bot.send_message(message.from_user.id, config.help_mes, reply_markup=help_kb)


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return await bot.send_message(message.from_user.id, 'Сейчас не происходит никаких действий.')
    await state.finish()
    await bot.send_message(message.from_user.id, 'Операция отменена. Не ошибайтесь, читайте /help.', reply_markup=greet_kb)

#reg handlers

@dp.message_handler(commands=['reg'])
async def cmd_start(message: types.Message):
    if str(message.from_user.id) not in db.get_id():
        await Form.username.set()
        await bot.send_message(message.from_user.id, "Введите никнейм. Условия никнеймов написаны в /help.")
    else:
        await bot.send_message(message.from_user.id, "У вас уже есть учётная запись. Перечитайте /help.", reply_markup=greet_kb)


@dp.message_handler(lambda message: message.from_user.id in db.get_id(), state=Form.username)
async def check_username(message: types.Message):
    return await bot.send_message(message.from_user.id, "Данное имя пользователя уже занято.\n\n> Для отмены напишите /cancel", reply_markup=cancel_kb)


@dp.message_handler(state=Form.username)
async def process_username(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['login'] = message.text

    await Form.next()
    await bot.send_message(message.from_user.id, "Введите пароль. Условия паролей находятся в /help.")


@dp.message_handler(lambda message: len(message.text) < 4, state=Form.pwd)
async def process_pwd_invalid(message: types.Message):
    return await bot.send_message(message.from_user.id, "Недопустимый пароль. Пожалуйста, введите другой или перечитайте /help.\n\n> Для отмены напишите /cancel.")


@dp.message_handler(state=Form.pwd)
async def process_pwd_repeat(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['pwd'] = message.text
        await bot.send_message(message.chat.id, 'Вы успешно зарегистрировались. Поздравляю, вы прочли /help!', reply_markup=greet_kb)
        db.add_log(data['login'], data['pwd'], message.from_user.id)
        await state.finish()

#login handlers 

@dp.message_handler(commands=['login']) 
async def login(message: types.Message):
    await Login.login.set()
    await bot.send_message(message.from_user.id, 'Введите ваш игровой ник', reply_markup=cancel_kb)


@dp.message_handler(lambda message: message.text not in db.get_logins() or db.check_auth(message.text), state=Login.login)
async def check_username(message: types.Message):
    if db.check_auth(message.text):
        return await bot.send_message(message.from_user.id, 'Данный пользователь уже онлайн.')
    else:
        return await bot.send_message(message.from_user.id, "Такого пользователя нет.\n\n> Для отмены напишите /cancel", reply_markup=cancel_kb)


@dp.message_handler(state=Login.login)
async def process_username(message: types.Message, state: FSMContext):
    async with state.proxy() as form:
        form['username'] = message.text

    await Login.next()
    await bot.send_message(message.from_user.id, "Введите пароль от учётной записи.")


@dp.message_handler(state=Login.pwd)
async def process_pwd_repeat(message: types.Message, state: FSMContext):
    async with state.proxy() as form:
        form['pwd'] = message.text
        if db.login(form['username'], form['pwd']):
            await bot.send_message(message.chat.id, 'Вы успешно авторизовались. Поздравляю, вы прочли /help!', reply_markup=greet_kb)
            await state.finish()
        else:
            await bot.send_message(message.chat.id, 'Неправильное имя пользователя или пароль. Перепроверьте.')
        
#logout handlers 
 
@dp.message_handler(commands=['logout'])
async def login(message: types.Message):
    await LogOut.login.set()
    await bot.send_message(message.from_user.id, 'Введите ваш игровой ник', reply_markup=cancel_kb)
    

@dp.message_handler(lambda message: message.text not in db.get_logins() or not db.check_auth(message.text), state=LogOut.login)
async def check_username(message: types.Message):
    if not db.check_auth(message.text):
        return await bot.send_message(message.from_user.id, 'Данный пользователь не онлайн.')
    else:
        return await bot.send_message(message.from_user.id, "Такого пользователя нет.\n\n> Для отмены напишите /cancel", reply_markup=cancel_kb)


@dp.message_handler(state=LogOut.login)
async def process_username(message: types.Message, state: FSMContext):
    async with state.proxy() as logout_form:
        logout_form['username'] = message.text

    await LogOut.next()
    await bot.send_message(message.from_user.id, "Введите пароль от учётной записи.")


@dp.message_handler(state=LogOut.pwd)
async def process_pwd_repeat(message: types.Message, state: FSMContext):
    async with state.proxy() as logout_form:
        logout_form['pwd'] = message.text
        if db.logout(logout_form['username'], logout_form['pwd']):
            await bot.send_message(message.chat.id, 'Вы успешно деавторизовались.', reply_markup=greet_kb)
            await state.finish()
        else:
            await bot.send_message(message.chat.id, 'Неправильное имя пользователя или пароль. Перепроверьте.', reply_markup=cancel_kb)


#send сборку 
@dp.message_handler(commands=['get'])
async def get_mods(message: types.Message):
    await bot.send_message(message.from_user.id, 'Вот ваша актуальная сборка. Прямо с печи!')
    await bot.send_document(message.from_user.id, config.mods_id, reply_markup=greet_kb) 
    print(message)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
=======
import json
import requests
import lxml
from bs4 import BeautifulSoup
import subprocess
import hashlib


def construct_offline_player_uuid(username):
    # extracted from the java code:
    # new GameProfile(UUID.nameUUIDFromBytes(("OfflinePlayer:" + name).getBytes(Charsets.UTF_8)), name));
    string = "OfflinePlayer:" + username
    hash = hashlib.md5(string.encode('utf-8')).digest()
    byte_array = [byte for byte in hash]
    # set the version to 3 -> Name based md5 hash
    byte_array[6] = hash[6] & 0x0f | 0x30
    # IETF variant
    byte_array[8] = hash[8] & 0x3f | 0x80

    hash_modified = bytes(byte_array)
    offline_player_uuid = add_uuid_stripes(hash_modified.hex())

    return offline_player_uuid


def add_uuid_stripes(string):
    string_striped = (
            string[:8] + '-' +
            string[8:12] + '-' +
            string[12:16] + '-' +
            string[16:20] + '-' +
            string[20:]
    )
    return string_striped


def whlsreload():
    pass
    # bashcom = "whitelist reload"
    # subprocess.Popen(bashcom, stdout=subprocess.PIPE)


def listToSrtConverter(lst):
    s = '[\n  {\n    "uuid": "%s",\n    "name": "%s"\n  }' % (lst[0]['uuid'], lst[0]['name'])
    for i in lst[1:]:
        s += ',\n  {\n    "uuid": "%s",\n    "name": "%s"\n  }' % (i['uuid'], i['name'])
    s += '\n]'
    return s


def get():
    with open('whitelist.json') as f:
        return f.read()


def repcheck(name):
    with open('whitelist.json') as f:
        if len(f.read()) == 0:
            return True
    with open('whitelist.json') as f:
        data = json.load(f)
    return len(list(filter(lambda x: x['name'] == name, data))) == 0


def put(name):
    if repcheck(name):
        to_json = get()
        uuid = construct_offline_player_uuid(name)
        if len(to_json) == 0:
            to_json = '[\n  {\n    "uuid": "%s",\n    "name": "%s"\n  }\n]' % (uuid, name)
            with open('whitelist.json', 'w') as f:
                f.write(to_json)
                whlsreload()
        else:
            to_json = get()[:-2] + ',\n  {\n    "uuid": "%s",\n    "name": "%s"\n  }\n]' % (uuid, name)
            with open('whitelist.json', 'w') as f:
                f.write(to_json)
                whlsreload()


def delete(name):
    if not repcheck(name):
        with open('whitelist.json') as f:
            data = json.load(f)
        to_del = list(filter(lambda x: x['name'] == name, data))[0]
        data.pop(data.index(to_del))
        with open('whitelist.json', 'w') as f:
            f.write(listToSrtConverter(data))
            whlsreload()


put('compot1')
# put('compot2')
# put('compot3')
# put('compot4')
# put('compot5')
# delete('compot4')
# print(get())
>>>>>>> d8c78dc (hui)
