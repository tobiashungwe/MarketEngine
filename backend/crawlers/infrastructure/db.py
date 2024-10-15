
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.company_model import Base, CompanyModel
import os
from dotenv import load_dotenv

class Database:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(__file__), '../../env/.env'))
        DATABASE_URL = os.getenv('DATABASE_URL')
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_company(self, company):
        session = self.Session()
        company_model = CompanyModel(
            name=company.name,
            email=company.email,
            address=company.address,
            industry=company.industry
        )
        session.add(company_model)
        session.commit()
        session.close()