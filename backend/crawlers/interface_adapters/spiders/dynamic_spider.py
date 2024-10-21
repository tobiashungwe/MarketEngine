import scrapy
from scrapy_selenium import SeleniumRequest
from ..items.company_item import CompanyItem

class DynamicSpider(scrapy.Spider):
    name = 'dynamic_spider'
    allowed_domains = ['dynamic-example.com']
    start_urls = ['https://dynamic-example.com/companies']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800
        },
        'SELENIUM_DRIVER_ARGUMENTS': ['--headless', '--disable-gpu'],
        'ROTATING_PROXY_LIST': [
            'proxy1.com:8000',
            'proxy2.com:8031'
        ],
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
        # Extract company links
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