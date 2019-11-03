# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from story.items import CrawlItem, NovelItem, NovelChapterItem, ChapterDetailItem


class StoryPipeline(object):
    """
        存储数据
    """
    def process_item(self, item, spider):
        return item







class MongoPipeline(object):
    """
        将item写入MongoDB
        """

    def __init__(self):
        self.client=pymongo.MongoClient(self.DB_URL)
        self.db= self.client[self.DB_NAME]



    #cls代表本身这个类


    @classmethod
    def from_crawler(cls, crawler):
        #默认是本地27017，当然具体看settings配置
        cls.DB_URL = crawler.settings.get('MONGO_DB_URI', 'mongodb://localhost:27017')
        cls.DB_NAME = crawler.settings.get('MONGO_DB_NAME', 'story')
        
        return cls()




    def open_spider(self, spider):
        '''
        爬虫一旦开启，就会实现这个方法，连接到数据库
        '''
        #print("啦啦啦啦啦绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿绿")
        self.client = pymongo.MongoClient(self.DB_URL)
        self.db = self.client[self.DB_NAME]

    def close_spider(self, spider):
        '''
        爬虫一旦关闭，就会实现这个方法，关闭数据库连接
        '''
        self.client.close()

    def process_item(self, item, spider):
        """ 判断item的类型，并作相应的处理，再入数据库 """
        if isinstance(item, CrawlItem):
            self._process_crawl(item)
        elif isinstance(item,NovelItem):
            self._process_novel(item)
        elif isinstance(item,NovelChapterItem):
            self._process_chapter(item)
        elif isinstance(item,ChapterDetailItem):
            self._process_detail(item)

        return item

    def _process_crawl(self, item):
        """
               存储爬虫信息
        """
        #去重，如果有小说名字，就不插入了
        collection = self.db['crawls']
        data = collection.find_one({
            'novel_id': item['novel_id']})
        if not data:
            collection.insert(dict(item))
        else:
            collection.save({'saved_num':item['saved_num']})






    def _process_novel(self, item):
        """
                       存储小说信息
        """
        collection = self.db['novels']
        data = collection.find_one({
            'novel_names': item['novel_name']})

        if not data:
            collection.insert(dict(item))




    def _process_chapter(self, item):
        """
                       存储章节
        """
        collection = self.db['chapters']
        data = collection.find_one({
            'novel_name': item['novel_name']})

        if not data:
            collection.insert(dict(item))





    def _process_detail(self, item):
        """
                       存储章节
        """





        collection = self.db['details']

        data = collection.find_one({
            'chapter_id': item['chapter_id']})

        print(self.db["chapters"].find_one({"novel_id": item["novel_id"]})["all_num"], "和呵呵哈哈哈或或或或或或或或或或或或或或或或",
              self.db["details"].find({"novel_id": item["novel_id"]}).count())

        if not data:
            collection.insert(dict(item))






        if self.db["chapters"].find_one({"novel_id": item["novel_id"]})["all_num"] == self.db["details"].find({"novel_id":item["novel_id"]}).count():

            print("我也一样晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕晕")

            de_duplication = CrawlItem()
            de_duplication["saved_num"] = self.db["details"].find({"novel_id":item["novel_id"]}).count()
            de_duplication["novel_id"] =item["novel_id"]
            #de_duplication["novel_name"] = response.meta["novel_name"]
            self._process_crawl(de_duplication)









