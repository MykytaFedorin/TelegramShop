import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
CHANEL_ID = "@testchanel0502"
GROUP_ID = "@testgroup0502"

script_path = os.path.abspath(__file__)
data_dir_path = os.path.dirname(script_path)
