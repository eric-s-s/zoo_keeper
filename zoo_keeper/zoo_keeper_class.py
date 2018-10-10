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

    zoo_id = Column(Integer)
    favorite_monkey_id = Column(Integer)
    dream_monkey_id = Column(Integer)

    def __init__(self, name, age, zoo_id=None, favorite_monkey_id=None, dream_monkey_id=None):
        validator = Validator()
        validator.raise_value_errors(zoo_id, favorite_monkey_id, dream_monkey_id)
        self.name = name
        self.age = age
        self.zoo_id = zoo_id
        self.favorite_monkey_id = favorite_monkey_id
        self.dream_monkey_id = dream_monkey_id

    def to_dict(self):
        keys = ['name', 'age', 'zoo_id', 'favorite_monkey_id', 'dream_monkey_id']
        return {key: getattr(self, key) for key in keys}

    def set_attributes(self, **kwargs):
        """

        :raises ValueError: If value is illegal
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        Validator().raise_value_errors(self.zoo_id, self.favorite_monkey_id, self.dream_monkey_id)

    def confirm_status(self):
        """

        :raises ValueError: If any value has become illegal
        """
        validator = Validator()
        kwargs = {key: getattr(self, key) for key in
                  ('zoo_id', 'favorite_monkey_id', 'dream_monkey_id')}
        validator.raise_value_errors(**kwargs)

    def set_bad_attributes_to_none(self):
        validator = Validator()
        if not validator.is_dream_monkey_id_ok(self.dream_monkey_id, self.zoo_id):
            self.dream_monkey_id = None
        if not validator.is_favorite_monkey_ok(self.favorite_monkey_id, self.zoo_id):
            self.favorite_monkey_id = None
        if not validator.is_zoo_ok(self.zoo_id):
            self.zoo_id = None


if __name__ == '__main__':
    from zoo_keeper.session import safe_session, engine
    Base.metadata.create_all(engine)
    with safe_session() as session:
        keeper = ZooKeeper(name='joe', age=10)
        print(session.query(ZooKeeper).all())
        print(session.query(ZooKeeper).first().to_dict())
        keeper.set_attributes(age=11)
        keeper.set_attributes(zoo_id=1)
        keeper.set_attributes(favorite_monkey_id=1)
        keeper.set_attributes(dream_monkey_id=1)
        session.commit()
