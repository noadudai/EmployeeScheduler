from typing import List
from Models.Days_models.Day_schedule_model import DayScheduleModel


class WorkersWeekScheduleModel:
    def __init__(self, days_in_the_week: List[DayScheduleModel]):
        self.week = days_in_the_week
        self.solutions = []

    def add_solution(self, solution: List[DayScheduleModel]):
        self.solutions.append(solution)

