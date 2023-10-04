from typing import List

from Models.Employee_model import Employee
from Models.Workers_week_schedule import WorkersWeekScheduleModel


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