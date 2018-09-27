import requests

from zoo_keeper import USER, DB, KEEPER_TABLE, SERVER_URL
from zoo_keeper.server_requests import ServerRequests, BadUrl

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates

engine = create_engine("mysql://{}@localhost/{}".format(USER, DB),
                       encoding='latin1')


Session = sessionmaker(bind=engine)


Base = declarative_base()


class ZooKeeper(Base):
    __tablename__ = KEEPER_TABLE

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    age = Column(Integer, nullable=False)

    zoo_name = Column(String(30), unique=True)
    favorite_monkey = Column(Integer, unique=True)
    dream_monkey = Column(Integer, unique=True)

    def to_dict(self):
        keys = ['name', 'age', 'zoo_name', 'favorite_monkey', 'dream_monkey']
        return {key: getattr(self, key) for key in keys}

    @validates('favorite_monkey')
    def validate_favorite(self, key, monkey_id):
        return monkey_id

    """
    favorite monkey must be in zoo where you work. 
    dream monkey cannot be in zoo where you work. 
    name varchar
    age = int
    zoo = 
    """


