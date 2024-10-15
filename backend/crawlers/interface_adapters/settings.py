
import os


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
