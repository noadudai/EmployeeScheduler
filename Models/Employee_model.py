from typing import List
from Models.Days_model import Day


class Employee:

    instances = []  # List of type Employee

    def __init__(self, name: str, preferences: List[Day], priority: int,
                 is_new: bool, day_off: List[Day], day_off_request: bool):
        self.name = name
        self.preferences = preferences
        self.priority = priority
        self.is_new = is_new
        self.days_off = day_off
        self.day_off_requested = day_off_request
        self.__class__.instances.append(self)
