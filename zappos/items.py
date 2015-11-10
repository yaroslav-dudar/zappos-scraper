# -*- coding: utf-8 -*-

import scrapy

class Product(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    color_choices = scrapy.Field()
    size = scrapy.Field()
    price = scrapy.Field()
    images = scrapy.Field()
    url = scrapy.Field()
    sku = scrapy.Field()
    scrape_date = scrapy.Field()
    source = scrapy.Field()
    currency = scrapy.Field()
