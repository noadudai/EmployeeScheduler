from Models.Shifts_model import Shifts


# A method or attribute with a single underscore prefix is considered non-public.

# TODO: preferences as "Tuesday morning shift".
# TODO: day-offs as "Tuesday"

class Day:
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
        self.day = day_of_the_week
        self._initialize_shifts()

    def _init_morning_and_closing_shifts_sun_to_wed(self) -> None:
        self.morning_shift = Shifts(Day.MORNING_START_SHIFT_KEY, Day.MORNING_END_SHIFT_KEY)
        self.closing_shift = Shifts(Day.NIGHT_START_SHIFT_KEY, Day.NIGHT_END_SHIFT_KEY)

    def _init_weekend_morning_and_evening_shifts(self) -> None:
        self.morning_shift = Shifts(Day.WEEKEND_MORNING_START_SHIFT_KEY, Day.WEEKEND_MORNING_END_SHIFT_KEY)
        self.morning_backup_shift = Shifts(Day.WEEKEND_MORNING_BACKUP_KEY, Day.WEEKEND_MORNING_END_SHIFT_KEY)
        self.evening_shift = Shifts(Day.WEEKEND_EVENING_START_SHIFT_KEY, Day.EVENING_END_SHIFT_KEY)

    def _initialize_shifts(self) -> None:

        if self.day == "Monday":
            Day._init_morning_and_closing_shifts_sun_to_wed(self)
            self.evening_shift = Shifts(Day.DELIVERY_DAY_EVENING_START_SHIFT_KEY, Day.EVENING_END_SHIFT_KEY)

        elif self.day in ["Sunday", "Tuesday", "Wednesday"]:
            Day._init_morning_and_closing_shifts_sun_to_wed(self)
            self.evening_shift = Shifts("16:00", Day.EVENING_END_SHIFT_KEY)

        elif self.day == "Thursday":
            self.morning_shift = Shifts(Day.MORNING_START_SHIFT_KEY, Day.MORNING_END_SHIFT_KEY)
            self.evening_shift = Shifts(Day.DELIVERY_DAY_EVENING_START_SHIFT_KEY, Day.EVENING_END_SHIFT_KEY)
            self.evening_backup_shift = Shifts("19:30", "02:00")
            self.closing_shift = Shifts("21:30", "04:00")

        elif self.day == "Friday":
            Day._init_weekend_morning_and_evening_shifts(self)
            self.closing_shift = Shifts("21:30", Day.NIGHT_END_SHIFT_KEY)

        elif self.day == "Saturday":
            Day._init_weekend_morning_and_evening_shifts(self)
            self.closing_shift = Shifts(Day.NIGHT_START_SHIFT_KEY, Day.NIGHT_END_SHIFT_KEY)

        else:
            raise ValueError("Invalid day.")
