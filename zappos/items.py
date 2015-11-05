# -*- coding: utf-8 -*-

import scrapy

class Product(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    color_choices = scrapy.Field()
    size_choices = scrapy.Field()
    price = scrapy.Field()
    images = scrapy.Field()
    url = scrapy.Field()
    sku = scrapy.Field()
