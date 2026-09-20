import logging
import sys


def setup_logger(name: str = 'sphinx') -> logging.Logger:
    """Configures structured application logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
