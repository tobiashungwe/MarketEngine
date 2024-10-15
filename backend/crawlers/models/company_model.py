from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CompanyModel(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    industry = Column(String, nullable=True)

    def __repr__(self):
        return f"<Company(name={self.name}, email={self.email})>"
