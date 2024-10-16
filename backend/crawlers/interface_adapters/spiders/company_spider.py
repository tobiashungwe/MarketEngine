import scrapy
from scrapy_selenium import SeleniumRequest
from ..items.company_item import CompanyItem
from ...use_cases.crawl_companies import CrawlCompanies

class CompanySpider(scrapy.Spider):
    name = 'company_spider'
    allowed_domains = ['example.com']
    start_urls = ['https://example.com/companies']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800
        },
        'ROTATING_PROXY_LIST': [
            'proxy1.com:8000',
            'proxy2.com:8031',
            # Add more proxies as needed
        ],
        'USER_AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                wait_time=10,
                wait_until=scrapy_selenium.WaitUntil(
                    lambda driver: driver.find_element_by_css_selector("div.company-listing")
                )
            )

    def parse(self, response):
        for company in response.css('div.company-listing'):
            company_url = company.css('a::attr(href)').get()
            if company_url:
                yield SeleniumRequest(
                    url=company_url,
                    callback=self.parse_company
                )

    def parse_company(self, response):
        item = CompanyItem()
        item['name'] = response.css('h1::text').get().strip()
        email = response.css('a.email::attr(href)').get()
        if email:
            item['email'] = email.replace('mailto:', '').strip().lower()
        else:
            item['email'] = None
        item['address'] = response.css('div.address::text').get().strip()
        item['industry'] = response.css('div.industry::text').get().strip()
        yield item
