import datetime


class Shifts:

    def __init__(self, start_shift: str, end_shift: str):
        self.start_shift = datetime.datetime.strptime(start_shift, "%H:%M").time()  # datetime object from string
        self.end_shift = datetime.datetime.strptime(end_shift, "%H:%M").time()  # datetime object from string
        self.worker_name = ""

    def set_worker_name(self, name):
        self.worker_name = name

