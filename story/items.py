# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class CrawlItem(scrapy.Item):
    # 小说id
    novel_id = scrapy.Field()
    # 小说名
    novel_name = scrapy.Field()


    #数据库里面已经下载了多少的小说
    saved_num=scrapy.Field()



#这个类基本上就是这么个套路，一个逻辑
class NovelItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    """
        Attributes:
            book_id 用户名
            title 用户id
            description 位置
            url 行业
            chapters
             -link
             -title 章节标题
             -body  章节内容
        """
    #小说id
    novel_id=scrapy.Field()
    #小说名
    novel_name=scrapy.Field()
    #小说链接
    novel_url=scrapy.Field()
    #小说作者
    novel_author=scrapy.Field()
    #小说章节列表页URL
    chapter_url=scrapy.Field()
    #小说简介
    short_info=scrapy.Field()
    #小说总字数
    word_count=scrapy.Field()
    #小说类型
    category=scrapy.Field()
    #小说状态，是否已经完本
    status=scrapy.Field()
    #小数解释（备用）
    description=scrapy.Field()
    #最新章节
    latest_chapter=scrapy.Field()
    #最近更新时间2019-05-10
    latest_update=scrapy.Field()






class NovelChapterItem(scrapy.Item):

    #小说id
    novel_id=scrapy.Field()
    #小说名
    novel_name=scrapy.Field()
    #总章节
    all_num=scrapy.Field()
    #chapter_count=scrapy.Field()
    all_chapters=scrapy.Field()#章节列表




class ChapterDetailItem(scrapy.Item):
    # 章节id
    chapter_id = scrapy.Field()
    # 章节内容
    # 小说id
    novel_id = scrapy.Field()
    contents = scrapy.Field()
    real_title=scrapy.Field()
    #html存储
    html=scrapy.Field()
    saved_num=scrapy.Field()
