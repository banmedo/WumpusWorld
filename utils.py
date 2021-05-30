import logging
LOG_FILE = "log.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, filemode="w")

def log(message, level=logging.INFO):
    print(message)
    if level == logging.INFO:
        logging.info(message)
    else:
        logging.error(message)
