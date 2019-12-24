from datetime import datetime
import logging
from typing import Any, Callable


def get_current_time(format):
    return datetime.now().strftime(format)


def log_wrap(
    logging_func: Callable = logging.info,
    before_msg: str = "",
    after_msg: str = "",
    debug: bool = False
) -> Any:
    """Wrapper that gives a function a start and end logging message.

    Parameters
    ----------
        logging_func : func
            Pointer to the logging function intended to be used.
        before_msg : str
            Message passed to logging before the primary function is called.
        after_msg : str
            Message passed to logging after the primary function is called.
        debug : bool
            If true, a descriptive logging.debug message will be created.
    """
    def decorate(func):
        """ Decorator """
        def call(*args, **kwargs):
            """ Actual wrapping """
            if debug:
                logging.debug(
                    "{{{file_name}:{line_no}:{func_name}}}".format(
                        file_name=func.__code__.co_filename,
                        line_no=func.__code__.co_firstlineno,
                        func_name=func.__name__
                    )
                )
            if before_msg != "":
                logging_func(before_msg)
            result = func(*args, **kwargs)
            if after_msg != "":
                logging_func(after_msg)
            return result
        return call
    return decorate
