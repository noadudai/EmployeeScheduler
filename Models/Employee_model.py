from typing import List


class Employee:

    instances = []  # List of type Employee

    def __init__(self, name: str, preferences: List[List[int]], priority: int,
                 is_new: bool, day_off: List[int], day_off_request: bool):
        self.name = name
        self.preferences = preferences
        self.priority = priority
        self.is_new = is_new
        self.days_off = day_off
        self.day_off_requested = day_off_request
        self.__class__.instances.append(self)

    def set_preferences(self, preferences):
        self.preferences = preferences

    def set_priority(self, priority):
        self.priority = priority

    def set_is_new(self, is_new):
        self.is_new = is_new

