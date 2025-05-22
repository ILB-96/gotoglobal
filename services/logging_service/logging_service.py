import logging
import threading

from .color_format import color_formatter


class Log:
    """Logging Data to the terminal or files."""

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    files_locks: dict[str, threading.Lock] = {}
    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(color_formatter)
        logger.addHandler(stream_handler)

    @classmethod
    def generate_log_file(
        cls,
        *args,
        path: str,
        mode="w",
        sep="\n",
    ):
        r"""Generate a log file with the given arguments.

        Args:
            *args: Variable number of arguments to be written to the log file.
            path (str): The path of the log file.
            mode (str, optional): The mode in which the file should be opened. Defaults to "w".
            sep (str, optional): The separator to be used between arguments. Defaults to "\n".
        """
        cls.files_locks[path] = cls.files_locks.get(path, threading.Lock())
        with cls.files_locks[path]:
            with open(path, mode) as file:
                for arg in args:
                    file.write(str(arg) + sep)

    @classmethod
    def debug(cls, data):
        """Logs the provided data as an debug message.

        Parameters:
        - cls: The class object.
        - data: The data to be logged.

        Returns:
        None
        """
        cls.logger.debug(data, stacklevel=2)

    @classmethod
    def info(cls, data):
        """Logs the provided data as an info message.

        Parameters:
        - cls: The class object.
        - data: The data to be logged.

        Returns:
        None
        """
        cls.logger.info(data, stacklevel=2)

    @classmethod
    def warning(cls, data):
        """Logs a warning message.

        Parameters:
        - cls: The class object.
        - data: The data to be logged.

        Returns:
        None
        """
        cls.logger.warning(data, stacklevel=2)

    @classmethod
    def error(cls, data):
        """Logs a error message.

        Parameters:
        - cls: The class object.
        - data: The data to be logged.

        Returns:
        None
        """
        cls.logger.error(data, stacklevel=5)

    @classmethod
    def critical(cls, data):
        """Logs a error message.

        Parameters:
        - cls: The class object.
        - data: The data to be logged.

        Returns:
        None
        """
        cls.logger.critical(data, stacklevel=2)
