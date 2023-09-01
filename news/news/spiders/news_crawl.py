import scrapy
from datetime import timedelta, date
import re
import hanja
from hanja import hangul

'''
1. python = 3.8 버전으로 가상환경 생성
2. hanja 라이브러리 설치
3. scrapy 설치(conda install -c scrapinghub scrapy)
4. scrapy 실행(cmd 창에 입력) : scrapy crawl news -o '파일명'.csv -t csv

'''

#연합뉴스   news_office_checked=1001
#연합 인포맥스 news_office_checked=2227
#이데일리   news_office_checked=1018
#페이지     01 02 14 24 34 44 54 64 74 84

BASE_URL = 'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={}&sort=0&photo=0&field=0&pd=3&ds={}&de={}&mynews=1&office_type=2&office_section_code=8&news_office_checked={}&office_category=0&service_area=0&nso=so:r,p:from{}to{},a:all&start={}'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}

class NewsSpider(scrapy.Spider):
    name = 'news'

    def start_requests(self):

        pages = ['01', '02', '14', '24', '34', '44', '54', '64', '74', '84']
        company = [1001, 2227, 1018]
        keyword = '금리'

        start_date = date(2009, 1, 1)
        end_date = date(2009, 12, 31)
        delta = timedelta(days=1)
        search_day = start_date


        while search_day <= end_date:
            target_day = search_day.strftime('%Y.%m.%d')
            for com in company:
                for page in pages:
                    url = BASE_URL.format(keyword, target_day, target_day, com, target_day, target_day, page)
                    try:
                        yield scrapy.Request(url=url, callback=self.news_list, headers=headers)
                    except:
                        continue
            search_day += delta

    def news_list(self, response):
        detail_urls = response.css('div.info_group > a:nth-child(3)::attr(href)').getall()
        for detail_url in detail_urls:
            try:
                yield scrapy.Request(url=detail_url, callback=self.news_detail, headers=headers)
            except:
                continue

    def news_detail(self, response):
    
        title = response.css('#title_area > span::text').getall()
        date = response.xpath('//*[@id="ct"]/div[1]/div[3]/div[1]/div/span/text()').getall()
        contents = response.css('#dic_area::text').getall()
        
        def process_title(text):
            processed_text = hanja.translate(text, 'substitution') #한자 변환
            processed_text = re.sub(r'"|<.*?>|[\r\n\t]+|\s+|[#$^&*[\]{}<>/|』◇◆▲()""△''■□=·●]', ' ', processed_text)
            return processed_text.strip()
        
        def process_date(text):
            processed_text = re.sub(r'"|<.*?>|[\r\n\t]+|\s+', ' ', text)
            processed_text = re.sub(r'(\d{4}\.\d{2}\.\d{2}\.)\s.*', r'\1', processed_text) #시간 제거
            return processed_text.strip()

        def process_content(text):
            processed_text = re.sub(r'\S+@\S+', '', text)   #이메일 주소 제거
            processed_text = re.sub(r'"|<.*?>|[\r\n\t]+|\s+|[#$^&*[\]{}<>/|』◇◆▲()""△''■□=·●]', ' ', processed_text)   #특수문자 제거
            return processed_text.strip()

        title = process_title(' '.join(title))
        date = process_date(' '.join(date))
        contents = process_content(''.join(contents))

        yield {
            'title': title,
            'date': date,
            'contents': contents
        }
       
        
