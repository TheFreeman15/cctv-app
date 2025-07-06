# logger.py
import logging

# Create logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter and add to handler
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
ch.setFormatter(formatter)

# Add handler to logger
logger.addHandler(ch)
