from services import Scheduler
from src.goto import late_alert
if __name__ == "__main__":
    tasks = [(late_alert.run, 0)]
    scheduler = Scheduler( interval_minutes=15, tasks=tasks)
    scheduler.start()
