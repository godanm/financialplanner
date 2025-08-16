from sqlalchemy import create_engine, sessionmaker

DATABASE_URL = "sqlite:///financial_data.db"

def get_db_session():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    engine = create_engine(DATABASE_URL)
    # Create all tables in the database
    from .models import Base
    Base.metadata.create_all(engine)