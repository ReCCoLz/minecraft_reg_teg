import os
from bs4 import BeautifulSoup
import requests

dir_to_file = os.path.abspath('whiltelist.txt')


def getUuid(name):
    resp = requests.get(f'https://top-minecraft.com/tools/offline-uuid.php?username={name}')
    soup = BeautifulSoup(resp.text, 'lxml')
    tt = soup.find('b', class_="text-warning").text
    return tt


print(getUuid('ReCCoLz'))
    