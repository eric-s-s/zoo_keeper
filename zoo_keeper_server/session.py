from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from zoo_keeper_server import USER, DB


def create_session(host='localhost'):
    engine = create_engine("mysql://{}@{}/{}".format(USER, host, DB),
                           encoding='latin1')

    return sessionmaker(bind=engine)()


