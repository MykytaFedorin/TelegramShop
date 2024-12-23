import os
from dotenv import load_dotenv
from database.db_connection import App_DB_Connection
from app_logger import logger

load_dotenv()

CHANEL_ID = str(os.getenv("CHANEL_ID"))
GROUP_ID = str(os.getenv("GROUP_ID"))
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
DB_NAME = str(os.getenv("DATABASE_NAME"))
DB_PASSWORD = str(os.getenv("DATABASE_PASSWORD"))
DB_HOST = str(os.getenv("DATABASE_HOST"))
DB_USER = str(os.getenv("DATABASE_USER"))
DB_PORT = str(os.getenv("DATABASE_PORT"))
SHOP_ID = str(os.getenv("SHOP_ID"))
SHOP_SECRET_KEY = str(os.getenv("SHOP_SECRET_KEY"))
TELEGRAM_PAYMENT_TOKEN=str(os.getenv("TELEGRAM_PAYMENT_TOKEN"))
script_path = os.path.abspath(__file__)
data_dir_path = os.path.dirname(script_path)

root_categories = []

async def init_categories():
    '''initiate root_categories in config module'''
    logger.debug(f"init categories")
    global root_categories
    db = App_DB_Connection()
    await db.connect()
    categories = await db.fetch_all("category", 
                               ["id",
                                "category_name",
                                "parent_id"])
    await db.close()
    root_categories = categories
    logger.info("Были инициализированы корневые категории")


root_cat_titles = []
async def init_titles():
    global root_categories
    if root_categories:
        for cat in root_categories:
            root_cat_titles.append(cat["category_name"])
