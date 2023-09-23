from Models.Shifts_model import Shifts
from Models.Day_model import DayModel


# A method or attribute with a single underscore prefix is considered non-public.

# add preferences for example "Tuesday morning shift".
# add day-offs for example "Tuesday"

class DayScheduleModel(DayModel):
    DELIVERY_DAY_EVENING_START_SHIFT_KEY = "15:00"
    WEEKEND_MORNING_START_SHIFT_KEY = "09:15"
    WEEKEND_EVENING_START_SHIFT_KEY = "18:00"
    WEEKEND_MORNING_END_SHIFT_KEY = "18:00"
    WEEKEND_MORNING_BACKUP_KEY = "12:00"
    MORNING_START_SHIFT_KEY = "11:45"
    NIGHT_START_SHIFT_KEY = "19:30"
    MORNING_END_SHIFT_KEY = "16:00"
    EVENING_END_SHIFT_KEY = "22:00"
    NIGHT_END_SHIFT_KEY = "02:00"

    def __init__(self, day_of_the_week: str):
        super().__init__(day_of_the_week)
        self._initialize_shifts()

    def _init_morning_and_closing_shifts_sun_to_wed(self) -> None:
        self.morning_shift = Shifts(DayScheduleModel.MORNING_START_SHIFT_KEY, DayScheduleModel.MORNING_END_SHIFT_KEY)
        self.closing_shift = Shifts(DayScheduleModel.NIGHT_START_SHIFT_KEY, DayScheduleModel.NIGHT_END_SHIFT_KEY)
        self.shifts.append(self.morning_shift)
        self.shifts.append(self.closing_shift)

    def _init_weekend_morning_and_evening_shifts(self) -> None:
        self.morning_shift = Shifts(DayScheduleModel.WEEKEND_MORNING_START_SHIFT_KEY, DayScheduleModel.WEEKEND_MORNING_END_SHIFT_KEY)
        self.morning_backup_shift = Shifts(DayScheduleModel.WEEKEND_MORNING_BACKUP_KEY, DayScheduleModel.WEEKEND_MORNING_END_SHIFT_KEY)
        self.evening_shift = Shifts(DayScheduleModel.WEEKEND_EVENING_START_SHIFT_KEY, DayScheduleModel.EVENING_END_SHIFT_KEY)
        self.shifts.append(self.morning_shift)
        self.shifts.append(self.morning_backup_shift)
        self.shifts.append(self.evening_shift)

    def _initialize_shifts(self) -> None:

        if self.day == "Monday":
            DayScheduleModel._init_morning_and_closing_shifts_sun_to_wed(self)
            self.evening_shift = Shifts(DayScheduleModel.DELIVERY_DAY_EVENING_START_SHIFT_KEY, DayScheduleModel.EVENING_END_SHIFT_KEY)
            self.shifts.append(self.evening_shift)

        elif self.day in ["Sunday", "Tuesday", "Wednesday"]:
            DayScheduleModel._init_morning_and_closing_shifts_sun_to_wed(self)
            self.evening_shift = Shifts("16:00", DayScheduleModel.EVENING_END_SHIFT_KEY)
            self.shifts.append(self.evening_shift)

        elif self.day == "Thursday":
            self.morning_shift = Shifts(DayScheduleModel.MORNING_START_SHIFT_KEY, DayScheduleModel.MORNING_END_SHIFT_KEY)
            self.evening_shift = Shifts(DayScheduleModel.DELIVERY_DAY_EVENING_START_SHIFT_KEY, DayScheduleModel.EVENING_END_SHIFT_KEY)
            self.evening_backup_shift = Shifts("19:30", "02:00")
            self.closing_shift = Shifts("21:30", "04:00")
            self.shifts.append(self.morning_shift)
            self.shifts.append(self.morning_backup_shift)
            self.shifts.append(self.evening_shift)
            self.shifts.append(self.closing_shift)

        elif self.day == "Friday":
            DayScheduleModel._init_weekend_morning_and_evening_shifts(self)
            self.closing_shift = Shifts("21:30", DayScheduleModel.NIGHT_END_SHIFT_KEY)
            self.shifts.append(self.closing_shift)

        elif self.day == "Saturday":
            DayScheduleModel._init_weekend_morning_and_evening_shifts(self)
            self.closing_shift = Shifts(DayScheduleModel.NIGHT_START_SHIFT_KEY, DayScheduleModel.NIGHT_END_SHIFT_KEY)
            self.shifts.append(self.closing_shift)

        else:
            raise ValueError("Invalid day.")
