# import scrapy
# from datetime import datetime, timedelta
# from user_agent import generate_user_agent
# from urllib.parse import urljoin
# import hanja
# from hanja import hangul
# from .clean import *
# import re

# headers = {'User-Agent': generate_user_agent(os='win', device_type='desktop')}

# class NaverFinanceNewsSpider(scrapy.Spider):
#     name = 'finance'
#     allowed_domains = ['finance.naver.com']
    
#     def start_requests(self):
#         base_url = 'https://finance.naver.com/news/news_search.naver?rcdate=&q=%B1%DD%B8%AE&x=0&y=0&sm=all.basic&pd=4&stDateStart={}&stDateEnd={}&page={}'
#         start_date = datetime(2009, 1, 1)
#         end_date = datetime(2009, 1, 31)
#         current_page = 1

#         while start_date <= end_date:
#             date_str = start_date.strftime('%Y-%m-%d')
#             url = base_url.format(date_str, date_str, current_page)

#             yield scrapy.Request(url=url, callback=self.parse, headers=headers)

#             start_date += timedelta(days=1)
            

#     def parse(self, response):
#         if not response.css('#contentarea_left > div.newsSchResult > dl > dt.articleSubject'):  # 페이지가 없는 경우
#             return
#         else:
#             detail_urls = response.css('#contentarea_left > div.newsSchResult > dl > dd.articleSubject a::attr(href), dt.articleSubject a::attr(href)').getall()
#             for detail_url in detail_urls:
#                 try:
#                     base_url = 'https://finance.naver.com'
#                     absolute_url = urljoin(base_url, detail_url)
#                     yield scrapy.Request(url=absolute_url, callback=self.parse_detail, headers=headers)
#                 except Exception as e:
#                     print(e)
#                     continue
        
#         # current_url = response.url
#         # current_page = int(current_url.split('&page=')[1])
#         # next_page = current_page + 1
#         # next_url = current_url.split('&page=')[0] + '&page=' + str(next_page)
#         # yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

#         # 다음 페이지로 이동
#         current_url = response.url
#         current_page = int(current_url.split('&page=')[1])
#         next_page = current_page + 1
#         next_url = current_url.split('&page=')[0] + '&page=' + str(next_page)
        
#         # 다음 페이지가 있다면 그 페이지로 이동하고, 없다면 다음 날짜로 이동
#         if response.css('#contentarea_left > div.newsSchResult > dl > dt.articleSubject'):
#             yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)
#         else:
#             self.current_date += timedelta(days=1)
#             if self.current_date <= self.end_date:
#                 self.current_page = 1  # 페이지를 초기화
#                 date_str = self.current_date.strftime('%Y-%m-%d')
#                 base_url = 'https://finance.naver.com/news/news_search.naver?rcdate=&q=%B1%DD%B8%AE&x=0&y=0&sm=all.basic&pd=4&stDateStart={}&stDateEnd={}&page={}'
#                 url = base_url.format(date_str, date_str, self.current_page)
#                 yield scrapy.Request(url=url, callback=self.parse, headers=headers)

#     #상세 뉴스 페이지 내용 크롤링(제목, 날짜, 본문, 신문사)
#     def parse_detail(self, response):
#         title = response.xpath('//*[@id="contentarea_left"]/div[2]/div[1]/div[2]/h3/text()').get()
#         date = response.xpath('//*[@id="contentarea_left"]/div[2]/div[1]/div[2]/div/span/text()').get()
#         company = response.xpath('//*[@id="contentarea_left"]/div[2]/div[1]/div[1]/span/img/@alt').get()

#         #본문 p태그 유무에 따라 크롤링
#         content_texts = response.xpath('//*[@id="content"]/p/text()').getall()
#         contents = content_texts if content_texts else response.xpath('//*[@id="content"]/text()').getall()

#         cleaned_title = clean_title(title)
#         cleaned_date = clean_date(date)
#         cleaned_contents = ' '.join(clean_content(c) for c in contents)
#         cleaned_company = clean_company(company)

#         yield {
#             'date': cleaned_date,
#             'title': cleaned_title,
#             'company': cleaned_company,
#             'contents': cleaned_contents
#         }


#--------------------------------------------------------
import scrapy
from datetime import datetime, timedelta
from user_agent import generate_user_agent
from urllib.parse import urljoin
from .clean import *


headers = {'User-Agent': generate_user_agent(os='win', device_type='desktop')}

class NaverFinanceNewsSpider(scrapy.Spider):
    name = 'finance'
    allowed_domains = ['finance.naver.com']
    def __init__(self, *args, **kwargs):
        super(NaverFinanceNewsSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://finance.naver.com/news/news_search.naver?rcdate=&q=%B1%DD%B8%AE&x=0&y=0&sm=all.basic&pd=4&stDateStart={}&stDateEnd={}&page={}'
        self.current_date = datetime(2009, 1, 1)
        self.end_date = datetime(2009, 12, 31)
        self.current_page = 1

    def start_requests(self):
        #크롤링 시작 url 생성
        date_str = self.current_date.strftime('%Y-%m-%d')
        url = self.base_url.format(date_str, date_str, self.current_page)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        # 기사 목록이 없을 경우 다음 날짜로 넘어감
        if not response.css('#contentarea_left > div.newsSchResult > dl > dt.articleSubject'):
            self.current_date += timedelta(days=1)
            #다음 날짜가 종료 날짜 이전일 경우 다시 parse함수 실행
            if self.current_date <= self.end_date:
                self.current_page = 1
                date_str = self.current_date.strftime('%Y-%m-%d')
                url = self.base_url.format(date_str, date_str, self.current_page)
                yield scrapy.Request(url=url, callback=self.parse, headers=headers)
            return

        # 기사 목록이 있을 경우 기사 url 크롤링 진행
        detail_urls = response.css('#contentarea_left > div.newsSchResult > dl > dd.articleSubject a::attr(href), dt.articleSubject a::attr(href)').getall()
        for detail_url in detail_urls:
            try:
                absolute_url = urljoin('https://finance.naver.com', detail_url)
                yield scrapy.Request(url=absolute_url, callback=self.parse_detail, headers=headers)
            except Exception as e:
                print(e)
                continue

        # 다음 페이지로 넘어감
        self.current_page += 1
        date_str = self.current_date.strftime('%Y-%m-%d')
        next_url = self.base_url.format(date_str, date_str, self.current_page)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    #상세 뉴스 페이지 내용 크롤링(제목, 날짜, 본문, 신문사)
    def parse_detail(self, response):
        title = response.xpath('//*[@id="contentarea_left"]/div[2]/div[1]/div[2]/h3/text()').get()
        date = response.xpath('//*[@id="contentarea_left"]/div[2]/div[1]/div[2]/div/span/text()').get()
        company = response.xpath('//*[@id="contentarea_left"]/div[2]/div[1]/div[1]/span/img/@alt').get()

        #본문 p태그 유무에 따라 크롤링
        content_texts = response.xpath('//*[@id="content"]/p/text()').getall()
        contents = content_texts if content_texts else response.xpath('//*[@id="content"]/text()').getall()

        cleaned_title = clean_title(title)
        cleaned_date = clean_date(date)
        cleaned_contents = ' '.join(clean_content(c) for c in contents)
        cleaned_company = clean_company(company)

        yield {
            'date': cleaned_date,
            'title': cleaned_title,
            'company': cleaned_company,
            'contents': cleaned_contents
        }

    


        
