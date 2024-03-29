import os
import sched
import time

"""
Perform crawling tasks on a regular basis
this module defult starts crawler on the everyday

"""
scheduler = sched.scheduler(time.time, time.sleep)

def crawl_tasks(spider_name):
    os.system("scrapy crawl %s" % spider_name)


def crawl_sched(spider_name, interval):
    scheduler.enter(interval, 0, crawl_sched, (interval,))
    crawl_sched(spider_name)

if __name__ == "__main__":
    scheduler.enter(0, 0, crawl_sched,("simple_crawler", 86400,))
    scheduler.run()