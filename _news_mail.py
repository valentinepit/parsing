from pprint import pprint
from time import sleep

import requests
from lxml import html
from pymongo import MongoClient

url = 'https://news.mail.ru'
page_number = 0
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

client = MongoClient('localhost', 27017)
db = client['head_hunter']
p_vc = db.python_vacancies


def get_unit(_link):
    unit = {}
    response = requests.get(_link, headers=headers)
    news = html.fromstring(response.text)
    unit['title'] = news.xpath(".//h1/text()")[0]
    unit['source'] = news.xpath(".//span[contains(text(),'источник:')]/../a/span[@class='link__text']/text()")[0]
    unit['date'] = news.xpath(".//span[@datetime]/@datetime")[0]
    unit['link'] = _link
    sleep(3)
    return unit


def get_content(_data):
    links = _data.xpath(".//a[@class ='newsitem__title link-holder']/@href | .//a[@class ='link link_flex']/@href")
    theme = []
    for link in links:
        unit = get_unit(link)
        theme.append(unit)
    return theme


def get_news():
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)
    blocks = dom.xpath('//div[contains(@class ,  "cols__inner")]')
    news = db.news
    result_dict = {}
    for block in blocks:
        block_name = block.xpath(".//span[@class='hdr__inner']/text()")
        if block_name:
            block_name = block_name[0]
        else:
            # понимаю, что не оптимально
            block_name = block.xpath("./../../../..//span[@class='hdr__inner']/text()")[0]
        print(f'{block_name = }')
        content = get_content(block)
        try:
            if result_dict[block_name]:
                for item in content:
                    result_dict[block_name].append(item)
        except:
            result_dict[block_name] = content
        news.update_one(result_dict, {'$set': result_dict}, upsert=True)
    return news


def main():
    news = get_news()
    for i in news.find():
        pprint(i)


if __name__ == '__main__':
    main()
