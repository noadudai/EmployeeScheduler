from typing import List
from ortools.sat.python import cp_model

from Models.Days_models.Day_model import DayModel
from Models.Days_models.Day_schedule_model import DayScheduleModel
from Models.Days_models.Day_preferences_model import DayPreferencesModel
from Models.Constraint_model import ConstraintModel
from Models.Employee_model import Employee
from Models.Workers_week_schedule import WorkersWeekScheduleModel
from Models.Shifts_model import *


def create_schedule(employees: List[Employee], week_info: WorkersWeekScheduleModel):
    # The last time I checked there were 7 days in a week (LOL😂).
    NUMBER_OF_DAYS_A_WEEK_KEY = 7
    this_week = week_info

    # The 'Constraint Programming' model
    model = cp_model.CpModel()

    # A dictionary that will hold employees as a (employee, day, shift)  as a key, snd a
    # boolean value of 1 or 0 if that employee is working on that day on that shift.
    shifts = {}

    constraint_model = ConstraintModel(week_info, employees, model, shifts)

    # Adding variables and constraint to the model.
    constraint_model.one_employee_in_each_shift_constraint()
    constraint_model.at_most_one_shift_a_day_constraint()
    constraint_model.prevent_new_employees_working_together_constraint()
    constraint_model.no_more_that_6_working_days_a_week_constraint()
    constraint_model.employee_day_off_request_constraint()
    constraint_model.no_opening_shift_after_closing_shift_constraint()
    constraint_model.objective_function()

    # Creates the solver and solve.
    solver = cp_model.CpSolver()

    previous_solution = set()

    count = 0
    while count <= 4:
        number_of_shifts_this_week = {}
        for employee in employees:
            number_of_shifts_this_week[employee.name] = 0

        status = solver.Solve(model)

        if status == cp_model.OPTIMAL:
            solution_identifier = frozenset(
                (employee.name, day, shift.shift_type) for day in range(len(this_week.week)) for employee in employees for shift in this_week.week[day].shifts
                if solver.Value(shifts[(employee.name, day, shift.shift_type)])
            )

            if solution_identifier not in previous_solution:
                previous_solution.add(solution_identifier)

                solution_days = []
                print(f"Solution:{count}")
                for day in range(len(this_week.week)):
                    print("Day", day)
                    solution_days.append(DayScheduleModel(this_week.week[day].day, this_week.week[day].shifts))
                    for employee in employees:
                        for shift in solution_days[day].shifts:

                            if solver.Value(shifts[(employee.name, day, shift.shift_type)]):
                                number_of_shifts_this_week[employee.name] += 1

                                shift.set_worker_name(employee.name)

                                if this_week.week[day].day in [employee_preferences_day.day for employee_preferences_day in employee.preferences]:
                                    preference_day_index = [employee_preferences_day.day for employee_preferences_day in employee.preferences].index(this_week.week[day].day)
                                    if shift.shift_type in [preferred_shift.shift_type for preferred_shift in employee.preferences[preference_day_index].shifts]:
                                        print(f"{employee.name} works shift {shift.shift_type} (requested).")
                                        break
                                    else:
                                        print(
                                            f"{employee.name} works shift {shift.shift_type} (not requested).")
                                        break
                                else:
                                    print(f"{employee.name} works shift {shift.shift_type} (not requested).")
                                    break

                print()
                for name, shifts_this_week in number_of_shifts_this_week.items():
                    print(f"{name} got {shifts_this_week} shifts")

                print()
                print()
                count += 1

                week_info.add_solution(solution_days)
        else:
            print("No optimal solution found !")


def create_employee_list() -> List[Employee]:
    noa_sunday = DayPreferencesModel("Sunday", [Shifts(Shifts.EVENING_SHIFT_KEY)])
    noa_monday = DayPreferencesModel("Monday", [Shifts(Shifts.MORNING_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY)])
    noa_wednesday = DayPreferencesModel("Wednesday", [Shifts(Shifts.EVENING_SHIFT_KEY)])
    noa_thursday = DayPreferencesModel("Thursday", [Shifts(Shifts.EVENING_SHIFT_KEY)])
    noa_friday = DayPreferencesModel("Friday", [Shifts(Shifts.WEEKEND_MORNING_SHIFT_KEY), Shifts(Shifts.WEEKEND_MORNING_BACKUP_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY)])
    noa_saturday = DayPreferencesModel("Saturday", [Shifts(Shifts.WEEKEND_MORNING_SHIFT_KEY), Shifts(Shifts.WEEKEND_MORNING_BACKUP_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY)])

    chepo_sunday = DayPreferencesModel("Sunday", [Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])
    chepo_tuesday = DayPreferencesModel("Tuesday", [Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])
    chepo_wednesday = DayPreferencesModel("Wednesday", [Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])
    chepo_thursday = DayPreferencesModel("Thursday", [Shifts(Shifts.CLOSING_SHIFT_KEY)])
    chepo_friday = DayPreferencesModel("Friday", [Shifts(Shifts.WEEKEND_MORNING_SHIFT_KEY), Shifts(Shifts.WEEKEND_MORNING_BACKUP_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY)])
    chepo_saturday = DayPreferencesModel("Saturday", [Shifts(Shifts.WEEKEND_MORNING_SHIFT_KEY)])

    beny_sunday = DayPreferencesModel("Sunday", [Shifts(Shifts.CLOSING_SHIFT_KEY)])
    beny_tuesday = DayPreferencesModel("Tuesday", [Shifts(Shifts.CLOSING_SHIFT_KEY)])
    beny_wednesday = DayPreferencesModel("Wednesday", [Shifts(Shifts.MORNING_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])
    beny_thursday = DayPreferencesModel("Thursday", [Shifts(Shifts.THURSDAY_BACKUP_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])
    beny_friday = DayPreferencesModel("Friday", [Shifts(Shifts.WEEKEND_MORNING_SHIFT_KEY)])
    beny_saturday = DayPreferencesModel("Saturday", [Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])

    misha_monday = DayPreferencesModel("Monday", [Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])
    misha_tuesday = DayPreferencesModel("Tuesday", [Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])
    misha_wednesday = DayPreferencesModel("Wednesday", [Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])
    misha_thursday = DayPreferencesModel("Thursday", [Shifts(Shifts.THURSDAY_BACKUP_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])
    misha_friday = DayPreferencesModel("Friday", [Shifts(Shifts.WEEKEND_MORNING_BACKUP_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])
    misha_saturday = DayPreferencesModel("Saturday", [Shifts(Shifts.WEEKEND_MORNING_BACKUP_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])


    noa_preferences = [noa_sunday, noa_monday, noa_wednesday, noa_thursday, noa_friday, noa_saturday]
    chepo_preferences = [chepo_sunday, chepo_tuesday, chepo_wednesday, chepo_thursday, chepo_friday, chepo_saturday]
    beny_preferences = [beny_sunday, beny_tuesday, beny_wednesday, beny_thursday, beny_friday, beny_saturday]
    misha_preferences = [misha_monday, misha_tuesday, misha_wednesday, misha_thursday, misha_friday, misha_saturday]

    noa = Employee("Noa", noa_preferences, 5, False, [], False)
    chepo = Employee("Chepo", chepo_preferences, 4, False,[], False)
    beny = Employee("Beny", beny_preferences, 4, False, [DayModel("Thursday")], True)
    misha = Employee("Misha", misha_preferences, 2, True, [], False)

    return Employee.instances


if __name__ == "__main__":

    days = [DayScheduleModel("Sunday", [Shifts(Shifts.MORNING_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)]),
            DayScheduleModel("Monday", [Shifts(Shifts.MORNING_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)]),
            DayScheduleModel("Tuesday", [Shifts(Shifts.MORNING_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)]),
            DayScheduleModel("Wednesday", [Shifts(Shifts.MORNING_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)]),
            DayScheduleModel("Thursday", [Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.THURSDAY_BACKUP_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)]),
            DayScheduleModel("Friday", [Shifts(Shifts.WEEKEND_MORNING_SHIFT_KEY), Shifts(Shifts.WEEKEND_MORNING_BACKUP_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)]),
            DayScheduleModel("Saturday", [Shifts(Shifts.WEEKEND_MORNING_SHIFT_KEY), Shifts(Shifts.WEEKEND_MORNING_BACKUP_SHIFT_KEY), Shifts(Shifts.EVENING_SHIFT_KEY), Shifts(Shifts.CLOSING_SHIFT_KEY)])]

    solution = WorkersWeekScheduleModel(days)
    create_schedule(create_employee_list(), solution)

