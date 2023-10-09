from typing import List

from Models.Employee_model import Employee
from Models.Workers_week_schedule import WorkersWeekScheduleModel
from Models.Shifts_model import *


# A function that will add constraints based on the day and the employees in that day, preventing 2 new employees
# from being in the same shift together (evening and closing on Sun-Wed,
# morning and backup on Fri-San and evening and closing on Fri-Sat).
def add_constraint_of_no_2_employees(shift1, shift2, day: int, shifts: dict,
                                     employees: List[Employee], model):
    new_employee_1 = sum(shifts[(employee.name, day, shift1.__name__)] for employee in employees if employee.is_new)
    new_employee_2 = sum(shifts[(employee.name, day, shift2.__name__)] for employee in employees if employee.is_new)

    # The solver will try different combinations of values for these booleans while exploring the solution space
    # to find a valid assignment of employees to shifts that satisfies all constraints
    condition_shift1 = model.NewBoolVar(f"condition_shift1_{day}")
    condition_shift2 = model.NewBoolVar(f"condition_shift2_{day}")

    # if there's at least one new employee on shift1, condition_shift1 must be true,
    # and if there's no new employee on shift1, condition_shift1 must be false.
    model.Add(new_employee_1 >= 1).OnlyEnforceIf(condition_shift1)
    model.Add(new_employee_1 == 0).OnlyEnforceIf(condition_shift1.Not())

    model.Add(new_employee_2 >= 1).OnlyEnforceIf(condition_shift2)
    model.Add(new_employee_2 == 0).OnlyEnforceIf(condition_shift2.Not())

    # Implication: if there's a new employee on shift1, there cannot be a new employee on shift2
    model.AddBoolOr([condition_shift1.Not(), condition_shift2.Not()])


# A function that populates the given shifts dictionary to hold employees as a (employee, day, shift)  as a key, and a
# boolean value of 1 or 0 if that employee is working on that day on that shift.
def populate_shifts_dict_for_cp_model(employees: List[Employee], week_info: WorkersWeekScheduleModel, model, shifts):
    for employee in employees:
        for day in range(len(week_info.week)):
            for shift in week_info.week[day].shifts:
                # shift.__class__.__name__ == the name of the class (for example "MorningShift")
                shifts[(employee.name, day, shift.__class__.__name__)] = model.NewBoolVar(f"shift_employee{employee.name}_day{day}_shift{shift.__class__.__name__}")


# A constraint that there will be only one employee in each shift per day
def one_employee_in_each_shift_constraint(week_info: WorkersWeekScheduleModel, employees: List[Employee], model, shifts):
    for day in range(len(week_info.week)):
        for shift in week_info.week[day].shifts:
            model.AddExactlyOne(shifts[(employee.name, day, shift.__class__.__name__)] for employee in employees)


# A constraint that each employee works at most one shift per day
def at_most_one_shift_a_day_constraint(week_info: WorkersWeekScheduleModel, employees: List[Employee], model, shifts):
    for employee in employees:
        for day in range(len(week_info.week)):
            model.AddAtMostOne(shifts[(employee.name, day, shift.__class__.__name__)] for shift in week_info.week[day].shifts)


# A constraint that ensures that on a given day, there are is no new employee in evening shift and a new employee
# in closing shift, and in the weekends, no 2 new employee in morning and backup shifts.
def prevent_new_employees_working_together_constraint(week_info: WorkersWeekScheduleModel, employees: List[Employee],
                                                      model, shifts):
    for day in range(len(week_info.week)):
        if week_info.week[day].day != "Thursday":
            if any(isinstance(shift, EveningShift) for shift in week_info.week[day].shifts) and any(
                    isinstance(shift, ClosingShift) for shift in week_info.week[day].shifts):
                add_constraint_of_no_2_employees(EveningShift, ClosingShift, day, shifts, employees, model)
            if any(isinstance(shift, WeekendMorningShift) for shift in week_info.week[day].shifts) and any(
                    isinstance(shift, WeekendMorningBackupShift) for shift in week_info.week[day].shifts):
                add_constraint_of_no_2_employees(WeekendMorningShift, WeekendMorningBackupShift, day, shifts, employees, model)


# A constraint that ensures that each employee does not work more than 6 days in a week
def no_more_that_6_working_days_a_week_constraint(week_info: WorkersWeekScheduleModel, employees: List[Employee],
                                                  model, shifts):
    # The max working days for an employee in a week is 6 by law.
    max_working_days_in_a_week = 6

    total_shifts_worked = {}
    for employee in employees:
        total_shifts_worked[employee.name] = sum(shifts[(employee.name, day, shift.__class__.__name__)] for
                                                 day in range(len(week_info.week)) for
                                                 shift in week_info.week[day].shifts)

    for employee in employees:
        model.Add(total_shifts_worked[employee.name] <= max_working_days_in_a_week)


# A constraint that ensures that only an employee who asked for a day-off in advance will get that day off.
# And if not, the solver will assign an employee based on needs.
def employee_day_off_request_constraint(week_info: WorkersWeekScheduleModel, employees: List[Employee],
                                        model, shifts):
    for employee in employees:
        for day in range(len(week_info.week)):
            if day > 3 and week_info.week[day].day in [day_off.day for day_off in employee.days_off]:
                for shift in week_info.week[day].shifts:
                    model.Add(shifts[(employee.name, day, shift.__class__.__name__)] == 0).OnlyEnforceIf(
                        employee.day_off_requested)


# A constraint that ensures that an employee how is working on a closing shift,
# will not work a morning shift on the day after.
def no_opening_shift_after_closing_shift_constraint(week_info: WorkersWeekScheduleModel, employees: List[Employee],
                                        model, shifts):
    for day in range(1, len(week_info.week)):  # Start from mon (not the sun)
        for employee in employees:
            # A boolean indicating if the employee worked a closing shift yesterday.
            worked_closing_shift_yesterday = model.NewBoolVar(f"{employee.name}_worked_closing_shift_yesterday_day{day}")

            model.Add(worked_closing_shift_yesterday == shifts.get((employee.name, day - 1, ClosingShift.__name__), 0))

            # If worked_closing_shift_yesterday is true, the employee cannot work a morning shift on the current day
            if day >= 5:
                model.Add(worked_closing_shift_yesterday + shifts.get((employee.name, day, WeekendMorningShift.__name__), 0) <= 1)
            else:
                model.Add(worked_closing_shift_yesterday + shifts.get((employee.name, day, MorningShift.__name__), 0) <= 1)
