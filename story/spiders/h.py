

# -*- coding: utf-8 -*-
import scrapy
import re

from bs4 import BeautifulSoup

from story.items import NovelChapterItem, ChapterDetailItem


class TestSpider(scrapy.Spider):
    name = 'h'

    start_urls = ["https://www.x23us.com/html/73/73236/32906071.html"]


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')  # 传入解析器

        # for i in soup.find("dd",id="contents"):
        #     print(i.get_text())
        title=soup.select("#amain > dl > dd:nth-child(2) > h1")[0].get_text()


        for i in range(5):
            if i==3:
                continue
            print(i)

