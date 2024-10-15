
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ...models.company_model import CompanyModel
from ...entities.company import Company

class PostgreSQLPipeline:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(__file__), '../../../env/.env'))
        DATABASE_URL = os.getenv('DATABASE_URL')
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        self.engine.connect()

    def process_item(self, item, spider):
        session = self.Session()
        company = CompanyModel(
            name=item['name'],
            email=item['email'],
            address=item['address'],
            industry=item['industry']
        )
        session.add(company)
        session.commit()
        session.close()
        return item

    def close_spider(self, spider):
        self.engine.dispose()
