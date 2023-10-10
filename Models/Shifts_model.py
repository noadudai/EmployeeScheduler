class Shifts:
    MORNING_SHIFT_KEY = "morning"
    EVENING_SHIFT_KEY = "evening"
    CLOSING_SHIFT_KEY = "closing"
    WEEKEND_MORNING_SHIFT_KEY = "weekend morning"
    WEEKEND_MORNING_BACKUP_SHIFT_KEY = "weekend morning backup"
    THURSDAY_BACKUP_SHIFT_KEY = "thursday backup"

    def __init__(self, shift_type):
        self.worker_name = ""
        self.shift_type = shift_type

    def set_worker_name(self, name):
        self.worker_name = name
