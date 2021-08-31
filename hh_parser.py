from pprint import pprint
from pymongo import MongoClient

import requests
from bs4 import BeautifulSoup as bs

url = 'https://hh.ru/search/vacancy'
page_number = 0
params = {'fromSearchLine': 'true', 'st': 'searchVacancy', 'text': 'python', 'page': f'{page_number}'}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

client = MongoClient('localhost', 27017)
db = client['head_hunter']
p_vc = db.python_vacancies

# можно конечно взять и с какого-нибудь API,
usd = 73.51
kzt = 0.17


def convertation(data, cur):
    money = {}
    if 'от' in data:
        money['from'] = int(data[1]) * cur
        money['to'] = None
    elif 'до' in data:
        money['from'] = None
        money['to'] = int(data[1]) * cur
    elif '–' in data:
        money['from'] = int(data[0]) * cur
        money['to'] = int(data[2]) * cur
    return money

def clear(_payment):
    _payment = _payment.replace('\u202f', '').split()
    money = {}
    if _payment[-1] == 'KZT':
        money = convertation(_payment, kzt)
    elif _payment[-1] == 'USD':
        money = convertation(_payment, usd)
    elif _payment[-1] == 'руб.':
        money = convertation(_payment, 1)
    money['currency'] = 'руб.'
    return money


def mongo_insert(_vacancy):
    p_vc.update_one(_vacancy, {'$set': _vacancy}, upsert=True)

def preparation(_soup):
    vacancies = []
    list_vacancies = _soup.findAll('div', {'class': 'vacancy-serp-item__row_header'})
    for item in list_vacancies:
        vacancy = {}
        title = item.find('span', {'class': 'g-user-content'}).text
        try:
            raw_payment = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).text
            payment = clear(raw_payment)
        except:
            payment = {'from': None, 'to': None, 'currency': None}
        vacancy['title'] = title
        vacancy['money'] = payment
        mongo_insert(vacancy)
        vacancies.append(vacancy)
    return vacancies


def list_count(_soup):
    pg_buttons = _soup.findAll('a', {'data-qa': 'pager-page'})
    return int(pg_buttons[-1].text)


def find_money():
    value = int(input('Введите минимальный размер оплаты '))
    for item in p_vc.find({'money.currency': 'руб.'}):
        try:
            if item.get('money').get('from') >= value:
                pprint(item)
                continue
        except:
            try:
                if item.get('money').get('to') >= value:
                    pprint(item)
            except:
                continue


def main():
    response = requests.get(url, headers=headers, params=params)
    if response.status_code:
        job = []
        soup = bs(response.text, 'html.parser')
        max_lists = list_count(soup)
        job.append(preparation(soup))
        for page_number in range(1, max_lists):
            soup = bs(response.text, 'html.parser')
            job.append(preparation(soup))
    else:
        print(f'{response}')

    find_money()

if __name__ == '__main__':
    main()
