import scrapy
from scrapy_selenium import SeleniumRequest
from ..items.company_item import CompanyItem
from ...use_cases.crawl_companies import CrawlCompanies
from scrapy_selenium import SeleniumRequest
import time
import requests
import os

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
        driver = response.meta['driver']
        # Check for CAPTCHA
        if "captcha" in driver.page_source.lower():
            self.solve_captcha(driver)
            time.sleep(2)  # Wait for the CAPTCHA to be solved
            yield SeleniumRequest(
                url=response.url,
                callback=self.parse_company
            )
            return

        # Existing parsing logic
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
    
    def solve_captcha(self, driver):
        # Extract CAPTCHA image source
        captcha_image = driver.find_element_by_css_selector("img.captcha").get_attribute("src")
        # Download CAPTCHA image
        captcha_response = requests.get(captcha_image)
        with open("captcha.png", "wb") as f:
            f.write(captcha_response.content)
        
        # Send CAPTCHA to solving service
        api_key = os.getenv('CAPTCHA_API_KEY')
        with open("captcha.png", "rb") as f:
            response = requests.post(
                "http://2captcha.com/in.php",
                files={"file": f},
                data={"key": api_key, "method": "post"}
            )
        captcha_id = response.text.split('|')[1]

        # Poll for CAPTCHA result
        solved = False
        for _ in range(20):
            time.sleep(5)
            result = requests.get(
                f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}"
            ).text
            if result.startswith("OK|"):
                captcha_text = result.split('|')[1]
                driver.find_element_by_css_selector("input.captcha").send_keys(captcha_text)
                driver.find_element_by_css_selector("button.submit").click()
                solved = True
                break

        if not solved:
            self.logger.error("Failed to solve CAPTCHA")
