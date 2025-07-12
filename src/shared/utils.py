import os
import sys
import time
from typing import Dict
from datetime import datetime as dt

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
import asyncio
import time
from functools import wraps
import httpx
def parse_time(time_str: str, dt_format: str = "%Y-%m-%dT%H:%M:%S.%f") -> dt | None:
    try:
        if "." in time_str:
            # Normalize to microseconds (6 digits)
            base, frac = time_str.split(".")
            frac = (frac + "000000")[:6]  # pad to 6 digits
            time_str = f"{base}.{frac}"
        else:
            dt_format = "%Y-%m-%dT%H:%M:%S"
        return dt.strptime(time_str, dt_format)
    except ValueError:
        print('Error parsing time:', time_str)
        return None

    
async def fetch_data(request_url: str, x_token: str, payload: Dict) -> Dict:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Token": x_token
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(request_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Request error: {e}")
        return {}

def async_retry(retries=3, delay=1, allow_falsy=False):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    result = await func(*args, **kwargs)
                    if not allow_falsy and not result:
                        raise ValueError("Function returned a falsy value")
                    return result
                except Exception as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(delay)
                    else:
                        print(f"Function {func.__name__} failed after {retries} attempts")
                        # Optionally log the exception
                        print(f"Last exception: {e}")
                        

        return async_wrapper
    return decorator

def retry(retries=3, delay=1, allow_falsy=False):
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
        
