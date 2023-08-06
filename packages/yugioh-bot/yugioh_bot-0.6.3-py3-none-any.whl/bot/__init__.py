import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
try:
    from bot.debug_helpers.logger import LastRecordHandler

    last_record = LastRecordHandler()
    logger.addHandler(last_record)
except ImportError:
    pass

logger.addHandler(ch)
from ._version import get_versions

__version__ = get_versions()['version']
if '+' in __version__:
    clean_version = __version__[:__version__.index('+')]
else:
    clean_version = __version__
if clean_version == 0 or clean_version == '0':
    logger.fatal("Clean version is wrong (0) cannot be zero something happened")
    logger.fatal("Try running git reset --hard origin/master")
del get_versions


def fake_decorator(arg1=0, arg2=0, arg3=0):
    def calling_function(__function):
        """
        Fake Decorator
        """
        def wrapper(*args, **kwargs):
            return __function(*args, **kwargs)
        return wrapper
    return calling_function

default_timestamp = 86400