# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CommonItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    keywords = scrapy.Fielf()
    p_texts = scrapy.Field()
    url = scrapy.Field()
    crawled_timestamp = scrapy.Field() # Timestamp of crawl the current page
    links = scrapy.Field() # link list wich each element include URL
    simhash = scrapy.Field() # simhash code ,depend on title description keywords and link texts
