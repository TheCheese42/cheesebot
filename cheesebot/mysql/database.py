from mysql.connector import connect, Error
from pathlib import Path


def load_sql(name: str):
    path = Path(__file__).parent / "sql" / f"{name}.sql"
    with open(path, "r", encoding="utf-8") as fp:
        return fp.read()


def setup_mysql(host: str, username: str, password: str):
    try:
        with connect(
            host=host,
            user=username,
            password=password,
        ) as connection:
            ..
