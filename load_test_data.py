from contextlib import contextmanager
import os
import sys

from typing import Union
import csv
import mysql.connector as cnx


USER = 'keeper_guest'
DB = 'keeper'
TABLE = 'zoo_keeper'
KEEPER_DATA = 'keeper_data.csv'


def load_zoo_keeper(data_dir_path):
    data_path = os.path.join(data_dir_path, KEEPER_DATA)
    with safe_connection() as conn:
        cur = conn.cursor()

        lines = load_csv(data_path)
        converted = [convert_line(line) for line in lines]
        cmd = "INSERT INTO {} (name, age, zoo_name, favorite_monkey, dream_monkey) VALUES (%s, %s, %s, %s, %s)"
        for line in converted:
            cur.execute(cmd.format(TABLE), line)
        conn.commit()


def load_csv(file_path):
    with open(file_path, 'r', newline='') as f:
        csv_reader = csv.reader(f, delimiter=',', quotechar='"', doublequote=True, skipinitialspace=True)
        raw = [row for row in csv_reader if row and not row[0].startswith('#')]
    return raw


@contextmanager
def safe_connection():
    db = cnx.connect(user=USER, host='localhost', database=DB)
    try:
        yield db
    finally:
        db.close()


def convert_line(line):
    return [convert_value(value) for value in line]


def convert_value(value: str) -> Union[str, int, None]:
    if value.lower() == 'null':
        return None
    try:
        return int(value)
    except ValueError:
        return value


def main(sys_args):
    if len(sys_args) != 2:
        raise ValueError('Exactly one argument, "data_dir" must be provided')
    load_zoo_keeper(sys_args[1])


if __name__ == '__main__':
    main(sys.argv)
