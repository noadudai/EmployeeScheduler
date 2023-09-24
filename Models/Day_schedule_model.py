from Models.Shifts_model import MorningShift, ClosingShift, EveningShift, WeekendMorningShift, \
    ThursdayBackupShift, WeekendMorningBackupShift
from Models.Day_model import DayModel


# A method or attribute with a single underscore prefix is considered non-public.

class DayScheduleModel(DayModel):

    def __init__(self, day_of_the_week: str):
        super().__init__(day_of_the_week)
        self._initialize_shifts()

    # using polymorphism, so that the shifts list will have a list of different shift types.
    def _init_shifts_sun_to_wed(self) -> None:
        self.shifts.append(MorningShift())
        self.shifts.append(EveningShift())
        self.shifts.append(ClosingShift())

    def _init_weekend_shifts(self) -> None:
        self.shifts.append(WeekendMorningShift())
        self.shifts.append(WeekendMorningBackupShift())
        self.shifts.append(EveningShift())
        self.shifts.append(ClosingShift())

    def _initialize_shifts(self) -> None:

        if self.day in ["Sunday", "Monday", "Tuesday", "Wednesday"]:
            DayScheduleModel._init_shifts_sun_to_wed(self)

        elif self.day == "Thursday":
            self.shifts.append(MorningShift())
            self.shifts.append(EveningShift())
            self.shifts.append(ThursdayBackupShift())
            self.shifts.append(ClosingShift())

        elif self.day in ["Friday", "Saturday"]:
            DayScheduleModel._init_weekend_shifts(self)

        else:
            raise ValueError("Invalid day.")
