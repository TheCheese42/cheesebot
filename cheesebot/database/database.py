from pathlib import Path
from typing import Any
from functools import cache

from exceptions import MalformedColumn
from lang import DEFAULT_LANGUAGE
from mysql.connector import Error, ProgrammingError, connect
from mysql.connector.types import ParamsSequenceOrDictType, RowType

DB_SCHEMA_TYPE = dict[
    str,
    tuple[
        tuple[
            str | int | None,
            ...
        ],
        ...
    ]
]
DB_SCHEMA: DB_SCHEMA_TYPE = {
    "server_config": (
        ('id', 'varchar(30)', 'NO', 'PRI', None, ''),
        ('lang_code', 'varchar(10)', 'NO', '', 'en_US', ''),
    ),
    "userdata_global": (
        ('id', 'varchar(30)', 'NO', 'PRI', None, ''),
        ('rickrolled', 'tinyint(1)', 'NO', '', '0', ''),
    ),
}


def load_sql(name: str):
    path = Path(__file__).parent / "sql" / f"{name}.sql"
    with open(path, "r", encoding="utf-8") as fp:
        return fp.read()


class CheeseDatabase:
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: str = "3306",
    ):
        self.connection = connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        self.cursor = self.connection.cursor()
        for table, fields in DB_SCHEMA.items():
            try:
                self.cursor.execute(f"DESCRIBE {table}")
            except ProgrammingError:
                # Table does not exist
                self.cursor.execute(load_sql(f"create_{table}"))
            else:
                # Table does exist, check for columns
                for i, (column, field) in enumerate(zip(self.cursor, fields)):
                    if column != field:
                        raise MalformedColumn(
                            f"Column {i} of MySQL table {table} is malformed. "
                            f"Expected {field}, got {column}."
                        )

    def execute_query(
        self,
        query: str,
        params: ParamsSequenceOrDictType = None
    ) -> None:
        self.ensure_connected()
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_data(
        self,
        query: str,
        params: ParamsSequenceOrDictType = None
    ) -> list[RowType]:
        self.ensure_connected()
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_value(
        self,
        table: str,
        id: str,
        field: str,
    ):
        result = self.fetch_data(
            f"SELECT {field} FROM {table} WHERE id = %s",
            params=(id,)
        )
        try:
            value = result[0][0]  # Twice cuz result is like `[("en_US",)]`
        except IndexError:
            value = None
        return value

    def update_or_create(
        self,
        table: str,
        id: str,
        field: str,
        value: Any,
    ):
        if self.fetch_data(
            f"SELECT * FROM {table} WHERE id = %s",
            params=(id,),
        ):
            self.execute_query(
                f"UPDATE {table} SET {field} = %s WHERE id = %s",
                params=(value, id),
            )
        else:
            self.execute_query(
                f"INSERT INTO {table} (id, {field}) VALUES (%s, %s)",
                params=(id, value),
            )

    @cache
    def get_langcode(self, guild_id: int | str | None = None) -> str:
        if guild_id is None:
            return DEFAULT_LANGUAGE

        code = self.fetch_value(
            table="server_config",
            id=str(guild_id),
            field="lang_code",
        )
        if code is None:
            return DEFAULT_LANGUAGE
        return code

    def ensure_connected(self):
        if not self.connection.is_connected():
            self.connection.reconnect(10)

    def close(self) -> None:
        self.cursor.close()
        self.connection.close()


def setup_mysql(
    host: str,
    port: str,
    username: str,
    password: str,
    database: str,
):
    """
    Setup an mysql database. ONLY USE THIS WHEN A DATABASE ISN'T SET UP YET.

    :param host: IP to the DB host.
    :type host: str
    :param port: Port to the DB host. Usually 3306.
    :type port: str
    :param username: Mysql username.
    :type username: str
    :param password: Mysql password.
    :type password: str
    :param database: Database name in the target server.
    :type database: str
    """
    try:
        with connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(load_sql("create_server_config"))
                cursor.execute(load_sql("create_userdata_global"))
    except Error:
        raise
