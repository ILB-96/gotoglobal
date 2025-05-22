import sys
import threading

from datetime import datetime


class ProgressBar:
    def __init__(self, total, desc="Progress", tasks=1):
        """Initialize the ProgressBar object.

        Args:
            total (int): The total number of iterations.
            desc (str, optional): The description of the progress. Defaults to "Progress".
            tasks (int, optional): The multiplier for displaying the completed iterations. Defaults to 1.
        """
        self.total, self.desc, self.tasks = total, desc, tasks
        self.iteration, self.data, self.start_time = 0, None, datetime.now()
        self._lock = threading.Lock()
        self.prev_iterations = 0

    def completed(self):
        return f"{self.iteration // self.tasks}/{self.total // self.tasks}(iter)"

    def output(self, percent, bar, completed):
        return f"\r\033[34m{percent}{bar} {completed} {self.data}      \r"

    def bar(self, bar_length=50):
        return f"|{"█" * (bar_length * self.iteration // self.total)}{"-" * (
            bar_length - (bar_length * self.iteration // self.total))}|"

    def set_iteration(self, n):
        if n == -1:
            self.iteration -= (self.iteration % self.tasks) - 1

        self.iteration += n

    def percent(self):
        return f"{self.desc}: {100 * (self.iteration / self.total):.1f}%"

    def __enter__(self):
        """Enter the context manager."""
        return self

    def update(self, n=1, prev=False, data=None, desc=None):
        with self._lock:
            if prev:
                self.prev_iterations = n
            if desc:
                self.desc = desc

            self.set_iteration(n)

            if not self.total or self.total - self.iteration < 0:
                return

            if data:
                self.data = f"[{data}]\033[0m"
            else:
                self.data = f"[{self.iter_per_minute()}/min]\033[0m"

            sys.stdout.write(self.output(self.percent(), self.bar(), self.completed()))
            sys.stdout.flush()

    def iter_per_minute(self):
        if (total_seconds := (datetime.now() - self.start_time).seconds) < 120:
            return self.iteration - self.prev_iterations
        return (self.iteration - self.prev_iterations) // (total_seconds // 60)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        # Ensure the progress bar moves to the next line when complete
        print()
