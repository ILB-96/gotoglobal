"""This module provides decorators for measuring execution time and retrying functions."""

import time
from functools import wraps

from playwright._impl._errors import TargetClosedError
from playwright.sync_api import TimeoutError as PWTimeout

from services import Log


def execution_time(func):
    """Decorator that measures the execution time of a function."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        except (KeyboardInterrupt, TargetClosedError):
            raise KeyboardInterrupt("User Keyboard interrupt.")
        except Exception as e:
            raise e
        finally:
            if (total_time := round((time.time() - start_time) / 60, 3)) < 2:
                Log.debug(
                    f"Execution time of {func.__name__}: {round(total_time * 60 )} seconds."
                )
            else:
                Log.debug(f"Execution time of {func.__name__}: {total_time} minutes.")

    return wrapper


def repeat_until_done(func):
    """Decorator that measures the execution time of a function."""

    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except (KeyboardInterrupt, TargetClosedError):
                raise KeyboardInterrupt("User Keyboard interrupt.")
            except (PWTimeout, TimeoutError):
                pass
            except Exception as e:
                Log.error(f"{e.__class__.__name__}: {e.args}")

    return wrapper


def retry(max_attempts=5, delay=5):
    """Retry decorator that retries a function a specified number of times with a delay between each attempt.

    Args:
        max_attempts (int): The maximum number of attempts.
        delay (int): The delay in seconds between each attempt.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except (KeyboardInterrupt, TargetClosedError):
                    raise KeyboardInterrupt("User Keyboard interrupt.")
                except Exception as e:
                    if "net::ERR_NAME_NOT_RESOLVED" not in str(e):
                        attempts += 1
                    if attempts == max_attempts:
                        raise e
                    time.sleep(delay)

        return wrapper

    return decorator
