import logging

from config.config import Config
from src.main_process import MainProcess

import warnings

warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default",
    category=UserWarning,
    module="openpyxl.styles.stylesheet"
)


if __name__ == "__main__":
    config: Config = Config.from_json()
    config.setup_logger()
    
    logger: logging.Logger = logging.getLogger(f"TaotianReport.{__name__}")
    
    logger.info("-"*50)
    logger.info("程序启动")
    
    mainprocess: MainProcess = MainProcess()
    mainprocess.run()
    
    logger.info("-"*50)
    logger.info("程序结束")