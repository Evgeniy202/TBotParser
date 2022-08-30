from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from cgitb import text
from bs4 import BeautifulSoup as BS
from datetime import date
import time
import requests
import sqlite3

import config


bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

work = False

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user_id = ''
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT user_id FROM users WHERE user_id = {message.from_user.id}")
    for user_id in cursor:
        user_id = user_id
        
    if user_id == '':
        cursor.execute(f"INSERT INTO users VALUES ('{message.from_user.id}')")
        conn.commit()
    
    conn.close()
    await bot.send_message(message.from_user.id, "Hellow! You have subscribed to a bot!")
    
@dp.message_handler(commands='run')
async def start_pars(messsage: types.Message):
    if messsage.from_user.id == config.ADMIN:
        await bot.send_message(messsage.from_id, "Run!")
        
        work = True
        
        while work == True:
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
                            
                            text = f"{name} to add new game: {tittle} \nhttps://plati.market{el.find('td', 'product-title').find('div').find('a')['href']}"
                            
                            print('New!!!')
                            
                            cursor.execute("SELECT * FROM users")
                            for id in cursor:
                                id = str(id).replace('(', '').replace(')', '').replace(',', '')
                                try:
                                    await bot.send_message(int(id), text)
                                except:
                                    cursor.execute(f"DELETE FROM users WHERE user_id = {int(id)}")
                    j+=1
                    
                    conn.commit()
                    
                if len(in_list) > 0:
                    for el in in_list:
                        cursor.execute(f"DELETE FROM datas WHERE name = '{name}' AND tittle = '{tittle}'")
                        conn.commit()

            conn.close
            
            time.sleep(30) 
            
@dp.message_handler(commands=['stop'])
async def stop_parser(message: types.Message):
    if message.from_user.id == config.ADMIN:
        work = False
        await bot.send_message(message.from_user.id, "Stop!")
    
def get_urls():
    with open('links.txt', 'r') as file:
        links = file.read()
    return links

if __name__ == '__main__':
    executor.start_polling(dp)