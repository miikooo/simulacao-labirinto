from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base() #base q o banco herda
engine = create_engine('sqlite:///labirintos.db')
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)