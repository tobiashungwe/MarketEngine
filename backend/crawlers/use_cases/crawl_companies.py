from ..entities.company import Company
from ..interface_adapters.spiders.company_spider import CompanySpider
from ..infrastructure.db import Database

class CrawlCompanies:
    def __init__(self):
        self.database = Database()

    def execute(self):
        spider = CompanySpider()
        companies = spider.run()
        for company_data in companies:
            company = Company(**company_data)
            self.database.save_company(company)