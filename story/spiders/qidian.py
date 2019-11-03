from datetime import datetime

import scrapy
from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError
from bs4 import BeautifulSoup
from story.items import CrawlItem, NovelItem, NovelChapterItem, ChapterDetailItem
import collections
import sys

from story.pipelines import MongoPipeline

sys.setrecursionlimit(1000000)

class QuotesSpider(scrapy.Spider):
    name = 'dingdian'
    #域名不在列表中的URL不会被跟进
    allowed_domains = ['x23us.com']
    mongoclient=None
    mongocollection=None
    saved_num=0





    #重写了父类的这个方法，所以如果上面还有start_urls，会直接失效，被重写了
    #建议不用start_urls，因为默认的dontfilter是true，就不会过滤掉初始化的这些url，导致后期request重复抓取
    def start_requests(self):
        #request异常处理
        #dont_filter去重，设置为false相同的地址会被过滤，不再请求
        self.mongoclient=MongoPipeline()
        self.mongocollection=self.mongoclient.db["crawls"]

        for category_id in range(1,11):
            request=Request(url="https://www.x23us.com/class/{}_1.html".format(str(category_id)),dont_filter=True,meta={"category_id":category_id},callback=self.get_allurls, method='GET',encoding='utf-8',errback=self.errback_httpbin)
            yield request

    #注意使用css选择器的时候爬取默认是没有tbody标签的，是浏览器自动加上去的，需要去除
    #解析这辈子都不用自带的了！！！！！！烂烂烂！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
    def get_allurls(self, response):
        #print(response.request.headers['User-Agent'])

        soup = BeautifulSoup(response.text, 'lxml')  # 传入解析器
        maxnum =soup.select("#pagelink > a.last")[0].get_text()#最大页
        category_id=response.meta["category_id"]




        #print(MongoPipeline().db["crawl"].count())


        for num in range(1, int(maxnum) + 1):
            url="https://www.x23us.com/class/" + str(category_id) + "_" + str(num) + ".html"

            yield Request(url,callback=self.get_novelurl,dont_filter=True,errback=self.errback_httpbin,meta={"category_id":category_id})


    def get_novelurl(self,response):

        soup = BeautifulSoup(response.text, 'lxml')  # 传入解析器
        trs = soup.select("#content > dd:nth-child(2) > table > tr:nth-child(n+2)")
        for tr in trs:

            novel_url=tr.find("a")["href"]
            novel_name=tr.find("a",target="_blank").string
            novel_id=int(novel_url.split("/")[-1])
            # item["category_id"]=int(response.meta["category_id"])
            # item["last_download"]="还没有开始下载章节"
            # item["percentage"]=0.0

            latestchapter=tr.select_one(" td:nth-child(2) > a").string
            chapter_url=tr.find("a",target="_blank")["href"]



            # 如果这部小说在数据库里面已经有了，就跳过
            if self.mongoclient.db["crawls"].find_one({"novel_id": novel_id}) != None:
                print("跳过小说",novel_name,"的下载")
                #continue
            else:
                print("没有",novel_name,"这部小说")

            yield Request(novel_url,callback=self.get_novelinfo,errback=self.errback_httpbin,meta={"novel_name":novel_name,"latestchapter":latestchapter,"chapter_url":chapter_url})
    #小说信息
    def get_novelinfo(self, response):
        item=NovelItem()
        soup = BeautifulSoup(response.text, 'lxml')  # 传入解析器



        item["novel_name"]=response.meta["novel_name"]
        item["novel_id"]=int(response.request.url.split("/")[-1])
        item["novel_url"]=response.request.url
        #吧nbsp空格去除
        item["novel_author"]=soup.select_one("#at > tr:nth-child(1) > td:nth-child(4)").string.replace("\u00a0", "")
        item["word_count"]=soup.select_one("#at > tr:nth-child(2) > td:nth-child(4)").string.replace("\u00a0", "")
        #可以找出这个节点的前面一个节点
        item["short_info"]=soup.select_one("#sidename").previous_sibling.string
        if item["short_info"]==None:
            item["short_info"]=""
        item["description"] =""
        item["category"]=soup.select_one("#at > tr:nth-child(1) > td:nth-child(2) > a").string

        item["status"]=soup.select_one("#at > tr:nth-child(1) > td:nth-child(6)").string.replace("\u00a0", "")
        item["latest_chapter"]=response.meta["latestchapter"]
        date=soup.select_one("#at > tr:nth-child(2) > td:nth-child(6)").string.replace("\u00a0", "")
        item["latest_update"] =datetime.strptime(date, '%Y-%m-%d')
        item["chapter_url"]=response.meta["chapter_url"]

        yield item








        yield Request(item["chapter_url"],callback=self.get_chapter,errback=self.errback_httpbin,meta={"novel_id":item["novel_id"],"novel_name":item["novel_name"]})
        # print("当前URL是"+item["wordcount"]
        #       +item["shortinfo"]+item["category"]+item["status"]+item["latestchapter"]+item["latestupdate"]
        #       )




    def get_chapter(self, response):
        item=NovelChapterItem()
        item["novel_id"] = response.meta["novel_id"]
        item["novel_name"] = response.meta["novel_name"]

        soup = BeautifulSoup(response.text, 'lxml')  # 传入解析器
        #saved=self.saved_num
        saved= 0






        #item["all_chapters"]=
        #print(response.request.url,response.request.headers['User-Agent'])


        #检查有木有多少卷那个标签
        part = soup.select("#at > tr > th")
        chapter=soup.select("#at > tr> td> a")

        trs=soup.select("#at > tr")

        part = "start"
        item["all_chapters"] = collections.OrderedDict()

        item["all_chapters"][part] = []
        for tr in trs:

            if tr.select(" th"):
                part = tr.select_one("th").string
                if trs[0]==tr:
                    item["all_chapters"] =collections.OrderedDict()





               # print("标签",tr.select_one("th").string)
                item["all_chapters"][part]=[]
               # print(item["all_chapters"])

            else:
                for a in tr.select("td > a"):

                    chapters_info= {
                        "chapter_url": response.request.url + a["href"],
                        "chapter_title": a.string,
                        "chapter_id": int( str(item["novel_id"]) + a["href"].split(".")[0] )
                    }

                    item["all_chapters"][part].append(chapters_info)
                    #print(response.request.url + a["href"])
                    # 去重设置


                    saved += 1




                    yield Request(response.request.url + a["href"], callback=self.get_chapter_detail,
                                  errback=self.errback_httpbin,meta={"chapter_id":int( str(item["novel_id"]) + a["href"].split(".")[0] ),"novel_id":item["novel_id"],"novel_name":item["novel_name"],"saved_num":saved})

        item["all_num"] = saved

        yield item
        # 已经爬好的放这里面










    def get_chapter_detail(self, response):

        soup = BeautifulSoup(response.text, 'lxml')  # 传入解析器

        item = ChapterDetailItem()
        item["contents"] = soup.find_all("dd", id="contents")[0].get_text()
        item["chapter_id"]=response.meta["chapter_id"]
        item["real_title"]=soup.select("#amain > dl > dd:nth-child(2) > h1")[0].get_text()
        item["novel_id"] = response.meta["novel_id"]
        item["saved_num"]=response.meta["saved_num"]

        yield item

        # if self.mongoclient.db["chapter"].find_one({"novel_id":response.meta["novel_id"]})["all_num"]==response.meta["saved_num"]:
        #     print(self.mongoclient.db["chapter"].find_one({"novel_id":response.meta["novel_id"]})["all_num"],"啛啛喳喳错错错错")
        #     de_duplication = CrawlItem()
        #     de_duplication["saved_num"] = response.meta["saved_num"]
        #     de_duplication["novel_id"] = response.meta["novel_id"]
        #     de_duplication["novel_name"]=response.meta["novel_name"]
            #yield de_duplication
















































    #404，DNS，超时
    def errback_httpbin(self, failure):
        # log all failures
        self.logger.info(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.info('HttpError错误 on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.info('DNSLookupError错误 on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.info('TimeoutError错误 on %s', request.url)