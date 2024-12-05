import psycopg2
from psycopg2 import sql
import data.config as app_data
from app_logger import logger
from typing import List, Dict


class App_DB_Connection:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                dbname=app_data.DB_NAME,
                user=app_data.DB_USER,
                password=app_data.DB_PASSWORD,
                host=app_data.DB_HOST,
                port=app_data.DB_PORT,
            )
            self.cursor = self.connection.cursor()
            logger.info("Connection with database established successfully")
        except Exception as ex:
            logger.error(f"Cannot establish connection with database: {ex}")
            raise

    def close(self) -> None:
        try:
            self.cursor.close()
            self.connection.close()
            logger.info("Connection with database was closed successfully")
        except Exception as ex:
            logger.error(f"Cannot close connection with database: {ex}")


def fetch_all(table: str, columns: List[str]) -> List[Dict]:
    """
    Fetch all rows from a specific table and return as a list of dictionaries.
    """
    db = None
    try:
        db = App_DB_Connection()
        cursor = db.cursor

        query = sql.SQL("SELECT {fields} FROM {table}").format(
            fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
            table=sql.Identifier(table),
        )
        cursor.execute(query)
        rows = cursor.fetchall()

        result = [
            {column: row[index] for index, column in enumerate(columns)}
            for row in rows
        ]
        return result
    except Exception as ex:
        logger.error(f"Error fetching data from table '{table}': {ex}")
        return []
    finally:
        if db:
            db.close()

