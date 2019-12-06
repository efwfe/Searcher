# -*- coding:utf-8 -*-

import datetime
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.mail import MailSender

class SendEmailExtension(object):

    def __init__(self, mailer, mail_to):
        self.mailer = mailer
        self.mail_to = mailer

        self.processed_items_numbers = 0

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings["MAIL_TO"]:
            raise NotConfigured("Not found configuration MAIL TO.")

        mailer = MailSender.from_settings(crawler.settings)
        ext    = cls(mailer, crawler.settings["MAIL_TO"])

        crawler.signals.connect(ext.spider_opened, signals.spider_opened)
        crawler.signals.connect(ext.spider_errored, signals.spider_error)
        crawler.signals.connect(ext.spider_closed, signals.spider_closed)
        crawler.signals.connect(ext.item_record, signals.item_passed)

        return ext
    
    def spider_opened(self, spider):
        subject = "%s began to crawl !" %spider.name
        body = """
            Hey guy, your crawler %s already crawling the data!
            date :%s
        """

        self.mailer.send(
            to = self.mailer,
            subject = subject,
            body = body %(spider.name, self.get_current_data())
        )

    
    def spider_closed(self, spider):
        subject = "%s already over !" %spider.name
        body = """
            Hey guy, your crawler %s already done its work ! 
            processed items numbers : %s
            date: %s

        """
        self.mailer.send(
            to = self.mailer,
            subject = subject,
            body = body %(spider.name, self.processed_items_numbers, self.get_current_data())
        )

    def spider_errored(self, failure, response, spider):
        subject = '%s come out error!' % spider.name
        body = """
               Hey guy, your crawler %s come out error when parse %s.
               error traceback: %s
               date: %s
               """
        body = body % (spider.name, response.url, failure.getTraceback(), self.get_current_date())

        self.mailer.send(
            to=self.mail_to,
            subject=subject,
            body=body
        )

    def item_record(self, item, spider):
        self.processed_items_numbers += 1

    def get_current_date(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')