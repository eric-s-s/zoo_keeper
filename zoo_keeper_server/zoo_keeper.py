from zoo_keeper_server import ZOO_KEEPER_TABLE
from zoo_keeper_server.validator import Validator
from zoo_keeper_server.zoo_service_request_handler import NoResponse

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

    def confirm_status(self):
        """

        :raises ValueError: If any value has become illegal
        """
        kwargs = {key: getattr(self, key) for key in
                  ('zoo_id', 'favorite_monkey_id', 'dream_monkey_id')}
        try:
            Validator().raise_value_errors(**kwargs)
        except NoResponse:
            pass

    def set_bad_attributes_to_none(self):
        validator = Validator()
        try:
            if not validator.is_dream_monkey_ok(self.dream_monkey_id, self.zoo_id):
                self.dream_monkey_id = None
            if not validator.is_favorite_monkey_ok(self.favorite_monkey_id, self.zoo_id):
                self.favorite_monkey_id = None
            if not validator.is_zoo_ok(self.zoo_id):
                self.zoo_id = None
        except NoResponse:
            pass


if __name__ == '__main__':
    from zoo_keeper_server.data_base_session import create_session
    session = create_session()
    try:
        keeper = ZooKeeper(name='joe', age=10)
        print(session.query(ZooKeeper).all())
        print(session.query(ZooKeeper).first().to_dict())
        keeper.set_attributes(age=11)
        keeper.set_attributes(zoo_id=1)
        keeper.set_attributes(favorite_monkey_id=1)
        keeper.set_attributes(dream_monkey_id=1)
        session.commit()
    finally:
        session.close()
