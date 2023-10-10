from typing import List, Dict
from ortools.sat.python.cp_model import CpModel

from Models.Employee_model import Employee
from Models.Workers_week_schedule import WorkersWeekScheduleModel
from Models.Shifts_model import *


class ConstraintModel:

    def __init__(self, week_info: WorkersWeekScheduleModel, employees: List[Employee], model: CpModel, shifts: Dict):
        self.week_info = week_info
        self.employees = employees
        self.model = model
        self.shifts = shifts
        self._populate_shifts_dict_for_cp_model()

    # A function that populates the given shifts dictionary to hold employees as a (employee, day, shift)  as a key,
    # and a boolean value of 1 or 0 if that employee is working on that day on that shift.
    def _populate_shifts_dict_for_cp_model(self):
        for employee in self.employees:
            for day in range(len(self.week_info.week)):
                for shift in self.week_info.week[day].shifts:
                    # shift.__class__.__name__ == the name of the class (for example "MorningShift")
                    self.shifts[(employee.name, day, shift.__class__.__name__)] = self.model.NewBoolVar(
                        f"shift_employee{employee.name}_day{day}_shift{shift.__class__.__name__}")

    # A function that will add constraints based on the day and the employees in that day, preventing 2 new employees
    # from being in the same shift together (evening and closing on Sun-Wed,
    # morning and backup on Fri-San and evening and closing on Fri-Sat).
    def _add_constraint_of_no_2_employees(self, shift1, shift2, day: int):
        new_employee_1 = sum(self.shifts[(employee.name, day, shift1.__name__)] for employee in self.employees if employee.is_new)
        new_employee_2 = sum(self.shifts[(employee.name, day, shift2.__name__)] for employee in self.employees if employee.is_new)

        # The solver will try different combinations of values for these booleans while exploring the solution space
        # to find a valid assignment of employees to shifts that satisfies all constraints
        condition_shift1 = self.model.NewBoolVar(f"condition_shift1_{day}")
        condition_shift2 = self.model.NewBoolVar(f"condition_shift2_{day}")

        # if there's at least one new employee on shift1, condition_shift1 must be true,
        # and if there's no new employee on shift1, condition_shift1 must be false.
        self.model.Add(new_employee_1 >= 1).OnlyEnforceIf(condition_shift1)
        self.model.Add(new_employee_1 == 0).OnlyEnforceIf(condition_shift1.Not())

        self.model.Add(new_employee_2 >= 1).OnlyEnforceIf(condition_shift2)
        self.model.Add(new_employee_2 == 0).OnlyEnforceIf(condition_shift2.Not())

        # Implication: if there's a new employee on shift1, there cannot be a new employee on shift2
        self.model.AddBoolOr([condition_shift1.Not(), condition_shift2.Not()])

    # A constraint that there will be only one employee in each shift per day
    def one_employee_in_each_shift_constraint(self):
        for day in range(len(self.week_info.week)):
            for shift in self.week_info.week[day].shifts:
                self.model.AddExactlyOne(self.shifts[(employee.name, day, shift.__class__.__name__)] for employee in self.employees)

    # A constraint that each employee works at most one shift per day
    def at_most_one_shift_a_day_constraint(self):
        for employee in self.employees:
            for day in range(len(self.week_info.week)):
                self.model.AddAtMostOne(self.shifts[(employee.name, day, shift.__class__.__name__)] for shift in self.week_info.week[day].shifts)

    # A constraint that ensures that on a given day, there are is no new employee in evening shift and a new employee
    # in closing shift, and in the weekends, no 2 new employee in morning and backup shifts.
    def prevent_new_employees_working_together_constraint(self):
        for day in range(len(self.week_info.week)):
            if self.week_info.week[day].day != "Thursday":
                if any(isinstance(shift, EveningShift) for shift in self.week_info.week[day].shifts) and any(
                        isinstance(shift, ClosingShift) for shift in self.week_info.week[day].shifts):
                    self._add_constraint_of_no_2_employees(EveningShift, ClosingShift, day)
                if any(isinstance(shift, WeekendMorningShift) for shift in self.week_info.week[day].shifts) and any(
                        isinstance(shift, WeekendMorningBackupShift) for shift in self.week_info.week[day].shifts):
                    self._add_constraint_of_no_2_employees(WeekendMorningShift, WeekendMorningBackupShift, day)

    # A constraint that ensures that each employee does not work more than 6 days in a week
    def no_more_that_6_working_days_a_week_constraint(self):
        # The max working days for an employee in a week is 6 by law.
        max_working_days_in_a_week = 6

        total_shifts_worked = {}
        for employee in self.employees:
            total_shifts_worked[employee.name] = sum(self.shifts[(employee.name, day, shift.__class__.__name__)] for
                                                     day in range(len(self.week_info.week)) for
                                                     shift in self.week_info.week[day].shifts)

        for employee in self.employees:
            self.model.Add(total_shifts_worked[employee.name] <= max_working_days_in_a_week)

    # A constraint that ensures that only an employee who asked for a day-off in advance will get that day off.
    # And if not, the solver will assign an employee based on needs.
    def employee_day_off_request_constraint(self):
        for employee in self.employees:
            for day in range(len(self.week_info.week)):
                if day > 3 and self.week_info.week[day].day in [day_off.day for day_off in employee.days_off]:
                    for shift in self.week_info.week[day].shifts:
                        self.model.Add(self.shifts[(employee.name, day, shift.__class__.__name__)] == 0).OnlyEnforceIf(employee.day_off_requested)

    # A constraint that ensures that an employee how is working on a closing shift,
    # will not work a morning shift on the day after.
    def no_opening_shift_after_closing_shift_constraint(self):
        for day in range(1, len(self.week_info.week)):  # Start from mon (not the sun)
            for employee in self.employees:
                # A boolean indicating if the employee worked a closing shift yesterday.
                worked_closing_shift_yesterday = self.model.NewBoolVar(
                    f"{employee.name}_worked_closing_shift_yesterday_day{day}")

                self.model.Add(
                    worked_closing_shift_yesterday == self.shifts.get((employee.name, day - 1, ClosingShift.__name__), 0))

                # If worked_closing_shift_yesterday is true, the employee cannot work a morning shift on the current day
                if day >= 5:
                    self.model.Add(
                        worked_closing_shift_yesterday + self.shifts.get((employee.name, day, WeekendMorningShift.__name__),
                                                                    0) <= 1)
                else:
                    self.model.Add(worked_closing_shift_yesterday + self.shifts.get((employee.name, day, MorningShift.__name__),
                                                                          0) <= 1)

    def objective_function(self):
        objective_terms = []

        for employee in self.employees:
            for day in range(len(self.week_info.week)):
                for shift in self.week_info.week[day].shifts:
                    if self.week_info.week[day].day in [employee_preferences_day.day for employee_preferences_day in employee.preferences]:
                        preference_day_index = [employee_preferences_day.day for employee_preferences_day in employee.preferences].index(self.week_info.week[day].day)
                        if shift.__class__.__name__ in [preferred_shift.__class__.__name__ for preferred_shift in employee.preferences[preference_day_index].shifts]:
                            objective_terms.append(employee.priority * self.shifts[(employee.name, day, shift.__class__.__name__)])

        objective = sum(objective_terms)

        self.model.Maximize(objective)
