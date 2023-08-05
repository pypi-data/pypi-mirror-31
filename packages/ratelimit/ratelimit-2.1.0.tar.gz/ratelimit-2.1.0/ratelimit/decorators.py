from functools import wraps
from math import floor

import time
import sys
import threading

from ratelimit.exception import RateLimitException

# Use monotonic time if available, otherwise fall back to the system clock.
now = time.monotonic if hasattr(time, 'monotonic') else time.time

class RateLimitDecorator(object):
    '''
    Rate limit decorator class.
    '''
    def __init__(self, calls=15, period=900, clock=now):
        '''
        Instantiate a RateLimitDecorator with some sensible defaults. By
        default the Twitter rate limiting window is respected (15 calls every
        15 minutes).

        :param int calls: Maximum function invocations allowed within a time period. Must be a number greater than 0.
        :param float period: An upper bound time period (in seconds) before the rate limit resets. Must be a number greater than 0.
        :param function clock: An optional function retuning the current time. This is used primarily for testing.
        '''
        self.clamped_calls = max(1, min(sys.maxsize, floor(calls)))
        self.period = period
        self.clock = clock

        # Initialise the decorator state.
        self.last_reset = clock()
        self.num_calls = 0

        # Add thread safety.
        self.lock = threading.RLock()

    def __call__(self, func):
        '''
        Return a wrapped function that prevents further function invocations if
        previously called within a specified period of time.

        :param function func: The function to decorate.
        :return: Decorated function.
        :rtype: function
        '''
        @wraps(func)
        def wrapper(*args, **kargs):
            '''
            Extend the behaviour of the decoated function, forwarding function
            invocations previously called no sooner than a specified period of
            time. The decorator will raise an exception if the function cannot
            be called so the caller may implement a retry strategy such as an
            exponential backoff.

            :param args: non-keyword variable length argument list to the decorated function.
            :param kargs: keyworded variable length argument list to the decorated function.
            :raises: RateLimitException
            '''
            with self.lock:
                elapsed = self.clock() - self.last_reset
                period_remaining = self.period - elapsed

                # If the time window has elapsed then reset.
                if period_remaining <= 0:
                    self.num_calls = 0
                    self.last_reset = self.clock()

                # Increase the number of attempts to call the function.
                self.num_calls += 1

                # If the number of attempts to call the function exceeds the
                # maximum then raise an exception.
                if self.num_calls > self.clamped_calls:
                    raise RateLimitException('too many calls', period_remaining)

            return func(*args, **kargs)
        return wrapper

def sleep_and_retry(func):
    '''
    Return a wrapped function that rescues rate limit exceptions, sleeping the
    current thread until rate limit resets.

    :param function func: The function to decorate.
    :return: Decorated function.
    :rtype: function
    '''
    @wraps(func)
    def wrapper(*args, **kargs):
        '''
        Call the rate limited function. If the function raises a rate limit
        exception sleep for the remaing time period and retry the function.

        :param args: non-keyword variable length argument list to the decorated function.
        :param kargs: keyworded variable length argument list to the decorated function.
        '''
        try:
            return func(*args, **kargs)
        except RateLimitException as exception:
            time.sleep(exception.period_remaining)
            return func(*args, **kargs)
    return wrapper
