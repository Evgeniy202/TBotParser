from openpyxl.reader.excel import load_workbook
from bs4 import BeautifulSoup as BS
from datetime import date
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import time
import requests
import sqlite3

import config


bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

def pars():
    links = get_urls()
    links = links.split('\n')
    
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    
    for link in links:
        req = requests.get(link + '#ss=name&sp=1')
        html = BS(req.text, 'lxml')
        
        print(link + '#ss=name&sp=1')

        name = html.find('div', class_='content_center').find('h1').find('span').text
        
        list_now = []
        for el in cursor.execute("SELECT tittle FROM datas WHERE name = ?", (name,)):
            list_now.append(str(el).replace('(', '').replace(')', '').replace(',', '').replace("'", '').replace('"', ''))

        j = 1
        in_list = []
        while j < int(html.find('div', class_='pages_nav').find_all('a')[-1].text) + 1:
            print('j= ', j)
            req = requests.get(link, f'#ss=name&sp={j}')
            html = BS(req.text, 'lxml')
            for el in html.find('table', class_='goods-table-merchant').find('tbody').find_all('tr'):
                tittle = el.find('td', 'product-title').find('div').find('a').text
                if tittle.replace('(', '').replace(')', '').replace(',', '').replace("'", '').replace('"', '') not in list_now:
                    date_now = date.today()
                    tittle = tittle.replace('(', '').replace(')', '').replace(',', '').replace("'", '').replace('"', '')
                    cursor.execute(f"INSERT INTO datas ('date', 'tittle', 'name') VALUES (?, ?, ?)", (date_now, tittle, name))
                    in_list.append(tittle)
            j+=1
            
            conn.commit()
            
        if len(in_list) > 0:
            for el in in_list:
                cursor.execute(f"DELETE FROM datas WHERE name = '{name}' AND tittle = '{tittle}'")
                conn.commit()

    conn.close
    
    time.sleep(30)
    pars()
    
def get_urls():
    with open('links.txt', 'r') as file:
        links = file.read()
    return links

if __name__ == '__main__':
    pars()