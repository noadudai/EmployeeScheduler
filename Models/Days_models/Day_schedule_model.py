from Models.Days_models.Day_model import DayModel


class DayScheduleModel(DayModel):

    def __init__(self, day_of_the_week: str, shifts):
        super().__init__(day_of_the_week)
        self.shifts = shifts
