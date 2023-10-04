class Shifts:
    def __init__(self):
        self.worker_name = ""
        self.shift_type = ""

    def set_worker_name(self, name):
        self.worker_name = name


class MorningShift(Shifts):
    def __init__(self):
        super().__init__()

        self.shift_type = "morning"


class EveningShift(Shifts):
    def __init__(self):
        super().__init__()

        self.shift_type = "evening"


class ClosingShift(Shifts):
    def __init__(self):
        super().__init__()

        self.shift_type = "closing"


class ThursdayBackupShift(Shifts):
    def __init__(self):
        super().__init__()

        self.shift_type = "thursday backup"


class WeekendMorningShift(Shifts):
    def __init__(self):
        super().__init__()

        self.shift_type = "weekend morning"


class WeekendMorningBackupShift(Shifts):
    def __init__(self):
        super().__init__()

        self.shift_type = "weekend morning backup"
