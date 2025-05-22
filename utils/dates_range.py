import math
from datetime import datetime, timedelta
from typing import Generator


class DatesRange:
    def __init__(
        self,
        start: str | datetime,
        end: str | datetime,
        days=100,
        date_format="%d/%m/%Y",
    ):
        """Initialize the DatesRange object.

        Args:
            start (str | datetime): The start date in the format "%d/%m/%Y".
            end (str | datetime): The end date in the format "%d/%m/%Y".
            days (int, optional): The number of days in each batch. Defaults to 100.
            date_format (str, optional): The format of the dates. Defaults to "%d/%m/%Y".

        """
        self.start = (
            start
            if isinstance(start, datetime)
            else datetime.strptime(start, date_format)
        )
        self.end = (
            end if isinstance(end, datetime) else datetime.strptime(end, date_format)
        )
        self.batch_days = timedelta(days)

    def total_batches(self, tasks=1) -> int:
        """Return the total number of batches in the date range.

        Returns:
            int: Number of batches.
        """
        return math.ceil(len(self) / self.batch_days.days) * tasks

    def start_day_month_year(self) -> tuple[str, str, str]:
        """Return the start day, month, and year of the date range.

        Returns:
            tuple: A tuple containing the start day, month, and year.
        """
        return str(self.start.day), str(self.start.month), str(self.start.year)

    def end_day_month_year(self) -> tuple[str, str, str]:
        """Return the start day, month, and year of the date range.

        Returns:
            tuple: A tuple containing the start day, month, and year.
        """
        return str(self.end.day), str(self.end.month), str(self.end.year)

    def __iter__(self) -> Generator["DatesRange", None, None]:
        """Iterate over the date range.

        Yields:
            tuple: A tuple containing the current start and end dates.
        """
        curr_start = self.start
        curr_end = min(self.start + self.batch_days, self.end)
        while curr_start <= self.end:
            yield DatesRange(curr_start, curr_end, self.batch_days.days)
            curr_start = curr_end + timedelta(days=1)
            curr_end = min(curr_start + self.batch_days, self.end)

    def __len__(self):
        """Return the number of days in the date range."""
        return (self.end - self.start).days + 1

    def __str__(self):
        """Return a string representation of the DatesRange object."""
        return f"{self.start.strftime('%d/%m/%Y')} - {self.end.strftime('%d/%m/%Y')}"
