import threading
import schedule
import time


class Executor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.tick = 1
        self.work = True
        self.first_run_tasks = []

    def run(self):
        for task in self.first_run_tasks:
            task.execute()

        while self.work:
            schedule.run_pending()
            time.sleep(self.tick)

    def stop(self):
        """stops a thread"""
        self.work = False

    def every_seconds(self, seconds, task, first_run=True):
        schedule.every(seconds).seconds.do(task.execute)
        if first_run:
            self.first_run_tasks.append(task)

    def every_minutes(self, minutes, task, first_run=True):
        schedule.every(minutes).minutes.do(task.execute)
        if first_run:
            self.first_run_tasks.append(task)

    def every_hours(self, hours, task, first_run=True):
        schedule.every(hours).hours.do(task.execute)
        if first_run:
            self.first_run_tasks.append(task)