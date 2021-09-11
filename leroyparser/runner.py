from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroyparser.spiders.leroy import LeroySpider
from leroyparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroySpider, query='обои')
    process.start()
