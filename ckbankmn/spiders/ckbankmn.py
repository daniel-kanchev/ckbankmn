import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from ckbankmn.items import Article


class ckbankmnSpider(scrapy.Spider):
    name = 'ckbankmn'
    start_urls = ['https://www.ckbank.mn/page/news']

    def parse(self, response):
        links = response.xpath('//a[@class="yellowbutton margin-top-25"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="maintext fr-view "]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
