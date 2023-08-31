import scrapy
from datetime import timedelta, date


#연합뉴스   office_section_code=8&news_office_checked=1001
#연합 인포맥스 office_section_code=8&news_office_checked=2227
#이데일리   office_section_code=8&news_office_checked=1018
#페이지     01 02 14 24 34 44 54 64 74 84

BASE_URL = 'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={}&sort=0&photo=0&field=0&pd=3&ds={}&de={}&mynews=1&office_type=2&office_section_code=8&news_office_checked={}&office_category=0&service_area=0&nso=so:r,p:from{}to{},a:all&start={}'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}

class NewsSpider(scrapy.Spider):
    name = 'news'

    def start_requests(self):

        pages = ['01', '02', '14', '24', '34', '44', '54', '64', '74', '84']
        #'01', '02', '14', '24', '34', '44', '54', '64', '74', '84'
        dates = []
        urls = []
        company = [1001, 2227, 1018]
        keyword = '금리'

        start_date = date(2017, 1, 1)
        end_date = date(2017, 8, 31)
        delta = timedelta(days=1)
        search_day = start_date


        while search_day <= end_date:
            target_day = search_day.strftime('%Y.%m.%d')
            dates.append(target_day)
            for com in company:
                for page in pages:
                    url = BASE_URL.format(keyword, target_day, target_day, com, target_day, target_day, page)
                    urls.append(url)
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
            except Exception as e:
                continue

    def news_detail(self, response):
    
        title = response.css('#title_area > span::text').getall()
        date = response.xpath('//*[@id="ct"]/div[1]/div[3]/div[1]/div/span/text()').getall()
        contents = response.css('#dic_area::text').getall()
        joined_contents = ' '.join(contents)
        
       
        for item in zip(title, date, [joined_contents]):
            title = item[0].strip() if title else ''
            date = item[1].strip() if date else ''
            contents = item[2].strip() if contents else ''

            yield {
                'title': title,
                'date' : date,
                'contents' : contents
                }
        
        
