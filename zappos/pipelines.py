# -*- coding: utf-8 -*-

from scrapy.conf import settings

import pymongo

class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        item.setdefault('source', 'http://zappos.com/')
        item.setdefault('currency', 'USD')
        # TODO: filter items
        self.collection.insert(dict(item))
