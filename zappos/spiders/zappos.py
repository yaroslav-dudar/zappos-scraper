# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http.request import Request

from ..items import Product

from selenium import webdriver
import requests
import re

last_page = int(Selector(
    text=requests.get('http://www.zappos.com/sitemap?p=0').text).\
    css('.pagination .last a::text').extract()[0])


class ZapposSpider(CrawlSpider):
    name = 'zappos'
    start_urls = ['http://www.zappos.com/sitemap?p=%d' % page for page in range(1)]
    allowed_domains = ['zappos.com']

    def __init__(self, *args, **kwargs):
        super(ZapposSpider, self).__init__(*args, **kwargs)
        self.browser = webdriver.Firefox()

    def parse(self, response):
        products = response.css('div#searchResults a.product::attr(href)').extract()
        
        for product in products[:1]:
            request = Request(
                'http://www.zappos.com/coach-box-program-signature-mini-id-skinny-sv-black-smoke-black',
                #'http://www.zappos.com%s' % product,
                dont_filter=True,
                callback=self.parse_product
            )

            yield request

    def parse_product(self, response):
        product = Product()
        product['name'] = response.css('span.ProductName::text').extract()[0]
        product['price'] = response.css('div#priceSlot span.price::text').extract()[0]
        product['sku'] = response.css('#sku span[itemprop=sku]::text').extract()[0]
        product['url'] = response.url
        product['brand'] = response.css('h1.banner meta[itemtype=brand]::attr(content)').extract()[0]
        product['category'] = response.xpath('//div[@id="breadcrumbs"]/a[contains(@class,"Breadcrumb*Category")]/text()').extract()[0]
        product['color_choices'] = response.css('div#colors option::text').extract()
        product['size_choices'] = response.xpath('//div[@id="dimension-size"]/select/option[@value!="-1_size"]/text()').extract()
        #product['description'] = self.parse_description(response)
        product['images'] = self.get_images_hrefs(response)

        # links to products with specific colors
        list_of_colors = response.css('#productImages a::attr(href)').extract()
        if len(list_of_colors) == 1 or not list_of_colors:
            # return item if only 1 color
            return product

        return Request(
            'http://www.zappos.com%s' % list_of_colors[1],
            dont_filter=True,
            meta={'product': product, 'list_of_colors': list_of_colors, 'pos': 1},
            callback=self.parse_images
        )

    def parse_description(self, response):
        rows = response.css('.description ul').xpath('descendant::text()').extract()
        if rows:
            return ' '.join(' '.join(rows).split())
        return ''

    def parse_images(self, response):
        product = response.meta['product']
        product['images'].extend(self.get_images_hrefs(response))

        if response.meta['pos'] + 1 == len(response.meta['list_of_colors']):
            return product

        pos = response.meta['pos'] + 1

        return Request(
            'http://www.zappos.com%s' % response.meta['list_of_colors'][pos],
            dont_filter=True,
            meta={'product': product, 'list_of_colors': response.meta['list_of_colors'], 'pos': pos},
            callback=self.parse_images
        ) 

    def get_images_hrefs(self, response):
        self.browser.get(response.url)
        import time
        time.sleep(5)

        img_urls = []
        for link in Selector(text=self.browser.page_source).css('#angles-list li a span::attr(style)').extract():
            img = re.match(".*\((http.*)\).*", link)
            if img:
                img_urls.append(img.group(1).replace('_THUMBNAILS', ''))

        return img_urls
