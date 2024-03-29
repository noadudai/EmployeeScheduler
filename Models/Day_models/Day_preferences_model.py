from typing import List
from Models.Day_models.Day_model import DayModel
from Models.Shifts_model import Shifts


class DayPreferencesModel(DayModel):
    def __init__(self, day_of_the_week: str, shifts: List[Shifts]):
        super().__init__(day_of_the_week)

        self.shifts = shifts
