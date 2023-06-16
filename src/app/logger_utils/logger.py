import logging

def get_logger():
    return logging.getLogger(__name__)

def log_info(logger, message):
    logger.info(message)
    
def log_warning(logger, message):
    logger.warning(message)
    
def log_error(logger, message):
    logger.error(message)

def log_critical(logger, message):
    logger.critical(message)
    
def log_debug(logger, message):
    logger.debug(message)
