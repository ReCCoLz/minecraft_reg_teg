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
