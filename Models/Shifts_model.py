import datetime


class Shifts:
    def __init__(self):
        self.worker_name = ""

    def set_worker_name(self, name):
        self.worker_name = name


class MorningShift(Shifts):
    def __init__(self):
        super().__init__()


class EveningShift(Shifts):
    def __init__(self):
        super().__init__()


class ClosingShift(Shifts):
    def __init__(self):
        super().__init__()


class ThursdayBackupShift(Shifts):
    def __init__(self):
        super().__init__()


class WeekendMorningShift(Shifts):
    def __init__(self):
        super().__init__()


class WeekendMorningBackupShift(Shifts):
    def __init__(self):
        super().__init__()
