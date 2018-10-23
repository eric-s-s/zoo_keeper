from flask import Flask

from zoo_keeper_server.data_base_session import DataBaseSession

from zoo_keeper_server import USER, DB

from sqlalchemy import create_engine


def create_app():
    app = Flask(__name__)
    app.config.from_object('zoo_keeper_server.flask_app_default_config')
    try:
        app.config.from_envvar('APP_CONFIG')
        print('using config:')
        print(app.config)
    except RuntimeError:
        print('using default config')

    app_engine = create_engine(
        "mysql://{}@{}/{}".format(USER, app.config.get('DB_HOST_NAME'), DB),
        encoding='latin1'
    )

    DataBaseSession.configure(bind=app_engine)

    return app
