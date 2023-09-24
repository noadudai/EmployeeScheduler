from typing import List

from Models.Day_model import DayModel
from Models.Day_preferences_model import DayPreferencesModel


class Employee:

    instances = []  # List of type Employee

    def __init__(self, name: str, preferences: List[DayPreferencesModel], priority: int,
                 is_new: bool, day_offs: List[DayModel], day_off_request: bool):
        self.name = name
        self.preferences = preferences
        self.priority = priority
        self.is_new = is_new
        self.days_off = day_offs
        self.day_off_requested = day_off_request
        self.__class__.instances.append(self)
