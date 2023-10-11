# Base class for DayPreferencesModel and DayScheduleModel
class DayModel:

    def __init__(self, day_of_the_week: str):
        self.day = day_of_the_week
        self.shifts = []
