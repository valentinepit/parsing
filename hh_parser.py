from pprint import pprint

import requests
from bs4 import BeautifulSoup as bs

url = 'https://hh.ru/search/vacancy'
page_number = 0
params = {'fromSearchLine': 'true', 'st': 'searchVacancy', 'text': 'python', 'page': f'{page_number}'}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}


def clear(_payment):
    money = {}
    _payment = _payment.replace('\u202f', '').split()
    money['currency'] = _payment[-1]

    if 'от' in _payment:
        money['from'] = int(_payment[1])
        money['to'] = None
    elif 'до' in _payment:
        money['from'] = None
        money['to'] = int(_payment[1])
    elif '–' in _payment:
        money['from'] = int(_payment[0])
        money['to'] = int(_payment[2])

    return money


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
        # print(vacancy)
        vacancies.append(vacancy)
    return vacancies


def list_count(_soup):
    pg_buttons = _soup.findAll('a', {'data-qa': 'pager-page'})
    return int(pg_buttons[-1].text)


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
        pprint(job)
    else:
        print(f'{response}')


if __name__ == '__main__':
    main()
