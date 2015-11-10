# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http.request import Request

from ..items import Product

import requests
import re
import datetime

last_page = int(Selector(
    text=requests.get('http://www.zappos.com/sitemap?p=0').text).\
    css('.pagination .last a::text').extract()[0])


class ZapposSpider(CrawlSpider):
    name = 'zappos'
    start_urls = ['http://www.zappos.com/sitemap?p=%d' % page for page in range(last_page)]
    allowed_domains = ['zappos.com']

    def __init__(self, *args, **kwargs):
        super(ZapposSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        products = response.css('div#searchResults a.product::attr(href)').extract()
        for product in products:
            request = Request(
                'http://www.zappos.com%s' % product,
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
        product['size'] = response.xpath('//div[@id="dimension-size"]/select/option[@value!="-1_size"]/text()').extract()
        product['description'] = self.parse_description(response)
        product['images'] = self.get_images_hrefs(response)
        product['scrape_date'] = datetime.datetime.now()

        # links to products with specific colors
        list_of_colors = self.filter_links(response.css('#productImages a::attr(href)').extract(), response.url)

        if not list_of_colors:
            # return item if only 1 color
            return product

        return Request(
            'http://www.zappos.com%s' % list_of_colors[0],
            dont_filter=True,
            meta={'product': product, 'list_of_colors': list_of_colors},
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

        list_of_colors = self.filter_links(response.meta['list_of_colors'], response.url)
        if not list_of_colors:
            return product

        return Request(
            'http://www.zappos.com%s' % list_of_colors[0],
            dont_filter=True,
            meta={'product': product, 'list_of_colors': list_of_colors},
            callback=self.parse_images
        ) 

    def get_images_hrefs(self, response):
        img_urls = []
        for link in response.css('#angles-list li a span::attr(style)').extract():
            img = re.match(".*\((http.*)\).*", link)
            if img:
                img_urls.append(img.group(1).replace('_THUMBNAILS', ''))

        return img_urls


    def filter_links(self, links, current_link):
        return filter(lambda link: link if link not in current_link and link != '#' else None, links)
