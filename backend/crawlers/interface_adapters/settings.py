
import os
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random

BOT_NAME = 'market_engine'

SPIDER_MODULES = ['backend.crawlers.interface_adapters.spiders']
NEWSPIDER_MODULE = 'backend.crawlers.interface_adapters.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 16

# Configure a delay for requests
DOWNLOAD_DELAY = 1

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'backend.crawlers.interface_adapters.pipelines.clean_pipeline.CleanCompanyDataPipeline': 300,
    'backend.crawlers.interface_adapters.pipelines.db_pipeline.PostgreSQLPipeline': 400,
}

# Enable AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10

# Configure retry settings
RETRY_ENABLED = True
RETRY_TIMES = 5
DOWNLOAD_TIMEOUT = 15

# Selenium settings
SELENIUM_DRIVER_NAME = os.getenv('SELENIUM_DRIVER_NAME', 'chrome')
SELENIUM_DRIVER_EXECUTABLE_PATH = os.getenv('SELENIUM_DRIVER_EXECUTABLE_PATH', '/usr/local/bin/chromedriver')
SELENIUM_DRIVER_ARGUMENTS = ['--headless', '--no-sandbox', '--disable-dev-shm-usage']


ROTATING_PROXY_LIST = [
    'proxy1.com:8000',
    'proxy2.com:8031',
    # Add more proxies as needed
]

DOWNLOADER_MIDDLEWARES.update({
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy_rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'scrapy_rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    'backend.crawlers.interface_adapters.middlewares.RandomUserAgentMiddleware': 400
})

# Scrapy Rotating Proxies Settings
ROTATING_PROXY_ENABLED = True
ROTATING_PROXY_CLOSE_SPIDER = True

