from typing import Callable, Iterable

import pandas as pd


def load_input_data(path: str, column: int = 0) -> list[str]:
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    # Check if the column index exists in the DataFrame
    if df.shape[1] <= column:
        return []

    # Return the selected column as a list
    return df.iloc[:, column].tolist()


def list_to_chunks(lst: list, n: int) -> list[list]:
    """Splits a list into n sublists."""
    k, m = divmod(len(lst), n)
    if k < 1:
        return [lst]
    return [lst[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n)]


def parse_dict_data(data: dict, default=""):
    """Parse the dictionary data and modify string values by stripping leading and trailing whitespace.

    Args:
        data (dict[str, any]): The dictionary data to be parsed.
        default (str): The default value to use if the dictionary value is empty.

    Returns:
        None
    """
    for key, value in data.items():
        val = value
        if isinstance(val, str):
            val = val.strip()
        data[key] = val if val else default


def iterate_over(rows: Iterable, callback: Callable):
    """Iterate over the rows and apply the callback function to each row.

    Args:
        rows: The rows to iterate over.
        callback: The callback function to apply to each row.

    Returns:
        None
    """
    list(map(callback, rows))
