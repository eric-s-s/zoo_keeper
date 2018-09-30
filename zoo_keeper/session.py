from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from zoo_keeper import USER, DB

engine = create_engine("mysql://{}@localhost/{}".format(USER, DB),
                       encoding='latin1')

Session = sessionmaker(bind=engine)


@contextmanager
def safe_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
