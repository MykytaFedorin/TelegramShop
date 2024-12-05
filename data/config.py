import os
from dotenv import load_dotenv

load_dotenv()

CHANEL_ID = str(os.getenv("CHANEL_ID"))
GROUP_ID = str(os.getenv("GROUP_ID"))
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
DB_NAME = str(os.getenv("DATABASE_NAME"))
DB_PASSWORD = str(os.getenv("DATABASE_PASSWORD"))
DB_HOST = str(os.getenv("DATABASE_HOST"))
DB_USER = str(os.getenv("DATABASE_USER"))
DB_PORT = str(os.getenv("DATABASE_PORT"))
script_path = os.path.abspath(__file__)
data_dir_path = os.path.dirname(script_path)
