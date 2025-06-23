import os
import sys
import time


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller-built .exe
    """
    try:
        # If running as a bundled app
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except AttributeError:
        # If running as a script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def retry(retries=3, delay=500, allow_falsy=False):
    """
    Decorator to retry a function call with a specified number of retries and delay.

    :param retries: Number of retries before giving up.
    :param delay: Delay between retries in seconds.
    :return: The result of the function if successful, otherwise raises the last exception.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    result = func(*args, **kwargs)
                    if not allow_falsy and not result:
                        raise ValueError("Function returned a falsy value")
                    return result
                except Exception:
                    if attempt < retries - 1:
                        time.sleep(delay)
            return "No result"
        return wrapper
    return decorator
        
