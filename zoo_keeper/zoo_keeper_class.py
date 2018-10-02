from functools import partial

from zoo_keeper import KEEPER_TABLE
from zoo_keeper.validator import Validator

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ZooKeeper(Base):
    __tablename__ = KEEPER_TABLE

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    age = Column(Integer, nullable=False)

    zoo_name = Column(String(50))
    favorite_monkey = Column(Integer)
    dream_monkey = Column(Integer)

    def __init__(self, name, age, zoo_name=None, favorite_monkey=None, dream_monkey=None):
        validator = Validator()
        validator.raise_value_errors(zoo_name, favorite_monkey, dream_monkey)
        self.name = name
        self.age = age
        self.zoo_name = zoo_name
        self.favorite_monkey = favorite_monkey
        self.dream_monkey = dream_monkey

    def to_dict(self):
        keys = ['name', 'age', 'zoo_name', 'favorite_monkey', 'dream_monkey']
        return {key: getattr(self, key) for key in keys}

    def set_attributes(self, **kwargs):
        """

        :raises ValueError: If value is illegal
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        Validator().raise_value_errors(self.zoo_name, self.favorite_monkey, self.dream_monkey)

    def confirm_status(self):
        """

        :raises ValueError: If any value has become illegal
        """
        validator = Validator()
        kwargs = {key: getattr(self, key) for key in
                  ('zoo_name', 'favorite_monkey', 'dream_monkey')}
        validator.raise_value_errors(**kwargs)

    def set_bad_attributes_to_none(self):
        validator = Validator()
        if not validator.is_dream_monkey_ok(self.dream_monkey, self.zoo_name):
            self.dream_monkey = None
        if not validator.is_favorite_monkey_ok(self.favorite_monkey, self.zoo_name):
            self.favorite_monkey = None
        if not validator.is_zoo_ok(self.zoo_name):
            self.zoo_name = None


if __name__ == '__main__':
    from zoo_keeper.session import safe_session, engine
    Base.metadata.create_all(engine)
    with safe_session() as session:
        keeper = ZooKeeper(name='joe', age=10)
        print(session.query(ZooKeeper).all())
        print(session.query(ZooKeeper).first().to_dict())
        keeper.set_attributes(age=11)
        keeper.set_attributes(zoo_name='Wacky Zachy\'s Monkey Attacky')
        keeper.set_attributes(favorite_monkey=1)
        keeper.set_attributes(dream_monkey=1)
        session.commit()