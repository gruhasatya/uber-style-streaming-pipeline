import logging

def get_logger(name:str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger



#### usage in files

# from utils.logging_utils import get_logger
# logger = get_logger("DispatchService")
# logger.info("Starting service...")
