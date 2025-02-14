import logging

def game_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
