from loguru import logger

logger.remove()
logger.add("logs.log", level="DEBUG")

