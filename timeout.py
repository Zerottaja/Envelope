"""This module contains a timeout function that kills another function
if its execution takes too long"""


import signal

from functools import wraps


def timeout():
    """timeout() contains a timer and a wrapper for the desired
    callable function. This function kills overdue executions."""

    def decorator(func):
        """decorator() is the new and modified function that calls
        the original function and contains the timer."""

        def __handle_timeout(signum, frame):
            """handle_timeout() determines what to do if the timer runs out."""

            del signum, frame  # we don't actually need these
            # time running out raises a TimeoutError
            raise TimeoutError("No immediate FIFO-packet found")

        def wrapper(*args, **kwargs):
            """wrapper() adds the extra bit of code (the timer) to
            the originally called function and calls it"""

            # specify the signal
            signal.signal(signal.SIGALRM, __handle_timeout)
            # set timer to 20 ms
            signal.setitimer(0, 0.02)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator
