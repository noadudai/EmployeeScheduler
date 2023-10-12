from typing import List

from Models.Day_models.Day_model import DayModel
from Models.Day_models.Day_preferences_model import DayPreferencesModel


class Employee:


    def __init__(self, name: str, preferences: List[DayPreferencesModel], priority: int,
                 is_new: bool, day_offs: List[DayModel], day_off_request: bool):
        self.name = name
        self.preferences = preferences
        self.priority = priority
        self.is_new = is_new
        self.days_off = day_offs
        self.day_off_requested = day_off_request

    def update_preferences(self, preferences: List[DayPreferencesModel]):
        self.preferences = preferences

    def update_day_offs(self, day_offs: List[DayModel], day_off_request: bool = False):
        # Default value of False, meaning the employee did not ask for a day off in advanced.
        self.days_off = day_offs
        self.day_off_requested = day_off_request
