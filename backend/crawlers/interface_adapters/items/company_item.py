import scrapy

class CompanyItem(scrapy.Item):
    name = scrapy.Field()
    email = scrapy.Field()
    address = scrapy.Field()
    industry = scrapy.Field()