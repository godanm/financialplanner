from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String)

class Income(Base):
    __tablename__ = 'income'
    
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

class Asset(Base):
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    current_value = Column(Float, nullable=False)
    type = Column(String)

class Liability(Base):
    __tablename__ = 'liabilities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

class FamilyMember(Base):
    __tablename__ = 'family_members'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    relation = Column(String, nullable=False)
    education_plan = Column(String)