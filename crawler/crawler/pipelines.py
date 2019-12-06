# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from twisted.internet.threads import deferToThread
from scrapy.exceptions import DropItem
from utils.simhash import Simhash

default_host = 'localhost'
default_port = 27017
default_db_name = '%(spider)s'
default_collection_name = '%(spider)s:items'


class MongodbPipeline:
    def __init__(self,
                url,
                host = default_host,
                port = default_port,
                db_name = default_db_name,
                collection_name = default_db_name
                )

        self.url = url if url else ""
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = colletion_name

    def open_spider(self, spider):
        """ Initialize mongodb client """
        if self.url == "":
            self.client = pymongo.MongoCient(self.host, self.port)
        else:
            self.client = pymongo.MongoClient(self.url)
        
        self.db_name, self.collection_name = self._replace_placeholder(spider)
        self.db = self.client[self.db_name]


    def close_spider(self, spider):
        self.client.close()

    def _replace_placeholder(self, spider):
        """
        returns replaced db_name and collection_name(base on spider name)
        if your db_name or collection_name does not have a placeholder 
        or db_name or collection name not base on spider name 
        you must override this function
        """
        return self.db_name %('spider': spdier.name), self.collection_name %(spdier:spider.name)

    @classmethod
    def from_settings(cls, settings):
        params = {}
        if settings.get("MONGODB_URL"):
            params["url"] = settings["MONGODB_URL"]
        if settigns.get("MONGODB_HOST"):
            params["host"] = settings["MONGODB_HOST"]
        if settings.get("MONGODB_PORT"):
            params["port"] = settings["MONGODB_PORT"]
        if settings.get("MONGODB_DB_NAME"):
            params["db_name"] = settings["MONGODB_DB_NAME"]
        if settings.get("MONOGDB_COLLECTION_NAME"):
            params["collection_name"] = settings["MONGODB_COLLECTION_NAME"]
        
        return cls(**params)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    def process_item(self, item, spider):
        return deferToThread(self._process_item_thread, item)

    def _process_item_thread(self, item):
        self.db[self.collection_name].insert_one(item)
        return item


class DuplicatesPipeline:
    """Validate item similarity by simhash and reject item that
    similarity greater than specify limit
    """

    def __init__(self):
        self.simhash_set = set()

    # TODO not efficient
    def process_item(self, item, spider):
        if item['simhash'] in self.simhash_set:
            raise DropItem("Duplicate item found : %s" % item)

        else:
            simhash = Simhash(item['simhash'])
            for other in self.simhash_set:
                if simhash.is_equal(other):
                    raise DropItem("Similarity high of the item : %s" % item)
            
        self.simhash_set.add(item['simhash'])
        return item