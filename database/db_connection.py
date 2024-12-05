import psycopg2
import data.config as app_data
from app_logger import logger

class App_DB_Connection():


    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                dbname=app_data.DB_NAME,  
                user=app_data.DB_USER,          
                password=app_data.DB_PASSWORD, 
                host=app_data.DB_HOST,         
                port=app_data.DB_PORT
            )
            self.cursor = self.connection.cursor()
            logger.info("Connection with database established succesfully")
        except Exception as ex:
            logger.error(f"Cannot established connection with database: {ex}")

    def close(self) -> None:
        try:
            self.cursor.close()
            self.connection.close()
            logger.info("Connection with database ws closed succesfully")
        except Exception as ex:
            logger.error(f"Cannot close connection with database {ex}")




