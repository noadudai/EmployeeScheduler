from typing import List
from Models.Day_schedule_model import DayScheduleModel


class WorkersWeekScheduleModel:
    def __init__(self, days_in_the_week: List[DayScheduleModel]):
        self.week = days_in_the_week
        # self.week = [DayScheduleModel("Sunday"), DayScheduleModel("Monday"), DayScheduleModel("Tuesday"),
        #              DayScheduleModel("Wednesday"), DayScheduleModel("Thursday"), DayScheduleModel("Friday"),
        #              DayScheduleModel("Saturday")]
