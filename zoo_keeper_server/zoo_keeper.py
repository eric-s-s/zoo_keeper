from zoo_keeper_server import ZOO_KEEPER_TABLE

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ZooKeeper(Base):
    __tablename__ = ZOO_KEEPER_TABLE

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    age = Column(Integer, nullable=False)

    zoo_id = Column(Integer)
    favorite_monkey_id = Column(Integer)
    dream_monkey_id = Column(Integer)

    def __init__(self, name, age, zoo_id=None, favorite_monkey_id=None, dream_monkey_id=None):
        self.name = name
        self.age = age
        self.zoo_id = zoo_id
        self.favorite_monkey_id = favorite_monkey_id
        self.dream_monkey_id = dream_monkey_id

    def to_dict(self):
        keys = ['id', 'name', 'age', 'zoo_id', 'favorite_monkey_id', 'dream_monkey_id']
        return {key: getattr(self, key) for key in keys}

    def set_attributes(self, **kwargs):
        """

        :raises ValueError: If value is illegal
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
