import asyncpg
from typing import List, Dict, Optional
import data.config as app_data
from app_logger import logger


class App_DB_Connection:
    def __init__(self):
        self.connection = None


    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        """
        Устанавливает соединение с базой данных.
        """
        try:
            self.connection = await asyncpg.connect(
                database=app_data.DB_NAME,
                user=app_data.DB_USER,
                password=app_data.DB_PASSWORD,
                host=app_data.DB_HOST,
                port=app_data.DB_PORT,
            )
            logger.info("Connection with database established successfully")
        except Exception as ex:
            logger.error(f"Cannot establish connection with database: {ex}")
            raise

    async def close(self) -> None:
        """
        Закрывает соединение с базой данных.
        """
        try:
            if self.connection:
                await self.connection.close()
                logger.info("Connection with database was closed successfully")
        except Exception as ex:
            logger.error(f"Cannot close connection with database: {ex}")

    async def fetch_all(self, table: str, columns: List[str]) -> List[Dict]:
        """
        Асинхронно получает все строки из таблицы и возвращает их в виде списка словарей.

        Args:
            table (str): Имя таблицы.
            columns (List[str]): Список колонок для выборки.

        Returns:
            List[Dict]: Список словарей, где каждый словарь представляет одну строку.
        """
        try:
            query = f"SELECT {', '.join(columns)} FROM {table}"
            rows = await self.connection.fetch(query)

            # Преобразование записей в список словарей
            return [dict(row) for row in rows]
        except Exception as ex:
            logger.error(f"Error fetching data from table '{table}': {ex}")
            raise

    async def fetch_raw(self, query: str, *params) -> Optional[List]:
        try:
            if self.connection:
                res = await self.connection.fetch(query, *params)
                if res:
                    return res
        except Exception as ex:
            logger.error(f"Ошибка выполнения сырого запроса: {ex}")

db = App_DB_Connection()
