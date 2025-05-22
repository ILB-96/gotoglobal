import sched
import signal
import time
from datetime import datetime, timedelta
from typing import Callable

from services import Log


class Scheduler:
    def __init__(self, interval_minutes: int = 15, tasks: list[tuple[Callable, int]] = None):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.interval_minutes = interval_minutes
        self.tasks = tasks or []
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        Log.critical(f"Signal {signum} received. Exiting scheduler gracefully...")
        raise KeyboardInterrupt("User Keyboard interrupt.")

    def _run_tasks(self):
        Log.info(f"Running tasks. Next run in {self.interval_minutes} minutes...")
        for func, mode in self.tasks:
            func(mode)
            Log.info("Tasks completed. Scheduling next run...")


        self.scheduler.enterabs(
            (datetime.now() + timedelta(minutes=self.interval_minutes)).timestamp(),
            1,
            self._run_tasks
        )

    def start(self):
        Log.info("Starting SchedulerService...")
        self.scheduler.enter(0, 1, self._run_tasks)
        try:
            self.scheduler.run()
        except KeyboardInterrupt:
            Log.info("Keyboard Interrupt. Press Ctrl + C to exit.")
        except Exception as e:
            Log.error(f"Scheduler error: {e}")
