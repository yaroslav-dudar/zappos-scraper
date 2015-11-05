# -*- coding: utf-8 -*-

# Scrapy settings for zappos project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'zappos'

SPIDER_MODULES = ['zappos.spiders']
NEWSPIDER_MODULE = 'zappos.spiders'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.6.3 (KHTML, like Gecko) Version/8.0.6 Safari/600.6.3'

CONCURRENT_REQUESTS_PER_DOMAIN = 2