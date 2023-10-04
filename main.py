from typing import List
from ortools.sat.python import cp_model

from Models.Day_model import DayModel
from Models.Employee_model import Employee
from Models.Day_schedule_model import DayScheduleModel
from Models.Day_preferences_model import DayPreferencesModel
from Models.Shifts_model import *  # ClosingShift, MorningShift, EveningShift, WeekendMorningShift, WeekendMorningBackupShift, ThursdayBackupShift
from Models.Workers_week_schedule import WorkersWeekScheduleModel
from constraints_file import *



def create_schedule(employees: List[Employee], week_info: WorkersWeekScheduleModel):
    # The last time I checked there were 7 days in a week (LOL😂).
    NUMBER_OF_DAYS_A_WEEK_KEY = 7
    this_week = week_info

    # The max working days for an employee in a week is 6 by law.
    max_working_days_in_a_week = 6

    # The 'Constraint Programming' model
    model = cp_model.CpModel()

    # Adding variables and constraints to the model:

    # A dictionary that will hold employees as a (employee, day, shift)  as a key, snd a
    # boolean value of 1 or 0 if that employee is working on that day on that shift.
    shifts = {}
    populate_shifts_dict_for_cp_model(employees, this_week, model, shifts)
    # for employee in employees:
    #     for day in range(len(this_week.week)):
    #         for shift in this_week.week[day].shifts:
    #             # shift.__class__.__name__ == the name of the class (for example "MorningShift")
    #             shifts[(employee.name, day, shift.__class__.__name__)] = model.NewBoolVar(f"shift_employee{employee.name}_day{day}_shift{shift.__class__.__name__}")

    # A constraint that there will be only one employee in each shift per day
    for day in range(len(this_week.week)):
        for shift in this_week.week[day].shifts:
            model.AddExactlyOne(shifts[(employee.name, day, shift.__class__.__name__)] for employee in employees)

    # A constraint that each employee works at most one shift per day
    for employee in employees:
        for day in range(len(this_week.week)):
            model.AddAtMostOne(shifts[(employee.name, day, shift.__class__.__name__)] for shift in this_week.week[day].shifts)

    # A constraint that ensures that on a given day, there are is no new employee in evening shift and a new employee
    # in closing shift, and in the weekends, no 2 new employee in morning and backup shifts.
    for day in range(len(this_week.week)):
        if this_week.week[day].day != "Thursday":
            if any(isinstance(shift, EveningShift) for shift in this_week.week[day].shifts) and any(
                    isinstance(shift, ClosingShift) for shift in this_week.week[day].shifts):
                add_constraint_of_no_2_employees(EveningShift, ClosingShift, day, shifts, employees, model)
            if any(isinstance(shift, WeekendMorningShift) for shift in this_week.week[day].shifts) and any(
                    isinstance(shift, WeekendMorningBackupShift) for shift in this_week.week[day].shifts):
                add_constraint_of_no_2_employees(WeekendMorningShift, WeekendMorningBackupShift, day, shifts, employees, model)

    # A constraint that ensures that each employee does not work more than 6 days in a week
    total_shifts_worked = {}
    for employee in employees:
        total_shifts_worked[employee.name] = sum(shifts[(employee.name, day, shift.__class__.__name__)] for
                                                 day in range(len(this_week.week)) for
                                                 shift in this_week.week[day].shifts)

    for employee in employees:
        model.Add(total_shifts_worked[employee.name] <= max_working_days_in_a_week)

    # A constraint that ensures that only an employee who asked for a day-off in advance will get that day off.
    # And if not, the solver will assign an employee based on needs.
    for employee in employees:
        for day in range(len(this_week.week)):
            if day > 3 and this_week.week[day].day in [day_off.day for day_off in employee.days_off]:
                for shift in this_week.week[day].shifts:
                    model.Add(shifts[(employee.name, day, shift.__class__.__name__)] == 0).OnlyEnforceIf(
                        employee.day_off_requested)

    # A constraint that ensures that an employee how is working on a closing shift,
    # will not work a morning shift on the day after.
    for day in range(1, len(this_week.week)):  # Start from mon (not the sun)
        for employee in employees:
            # A boolean indicating if the employee worked a closing shift yesterday.
            worked_closing_shift_yesterday = model.NewBoolVar(f"{employee.name}_worked_closing_shift_yesterday_day{day}")

            model.Add(worked_closing_shift_yesterday == shifts.get((employee.name, day - 1, ClosingShift.__name__), 0))

            # If worked_closing_shift_yesterday is true, the employee cannot work a morning shift on the current day
            if day >= 5:
                model.Add(worked_closing_shift_yesterday + shifts.get((employee.name, day, WeekendMorningShift.__name__), 0) <= 1)
            else:
                model.Add(worked_closing_shift_yesterday + shifts.get((employee.name, day, MorningShift.__name__), 0) <= 1)

    objective_terms = []

    for employee in employees:
        for day in range(len(this_week.week)):
            for shift in this_week.week[day].shifts:
                if this_week.week[day].day in [employee_preferences_day.day for employee_preferences_day in
                                                employee.preferences]:
                    preference_day_index = [employee_preferences_day.day for employee_preferences_day in
                                            employee.preferences].index(this_week.week[day].day)
                    if shift.__class__.__name__ in [preferred_shift.__class__.__name__ for preferred_shift in
                                                    employee.preferences[preference_day_index].shifts]:
                        objective_terms.append(employee.priority * shifts[(employee.name, day, shift.__class__.__name__)])

    objective = sum(objective_terms)

    model.Maximize(objective)

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
                (employee.name, day, shift.__class__.__name__) for day in range(len(this_week.week)) for employee in employees for shift in this_week.week[day].shifts
                if solver.Value(shifts[(employee.name, day, shift.__class__.__name__)])
            )

            if solution_identifier not in previous_solution:
                previous_solution.add(solution_identifier)

                print(f"Solution:{count}")
                for day in range(len(this_week.week)):
                    print("Day", day)
                    for employee in employees:
                        for shift in this_week.week[day].shifts:
                            if solver.Value(shifts[(employee.name, day, shift.__class__.__name__)]):
                                number_of_shifts_this_week[employee.name] += 1
                                if this_week.week[day].day in [employee_preferences_day.day for employee_preferences_day in employee.preferences]:
                                    preference_day_index = [employee_preferences_day.day for employee_preferences_day in employee.preferences].index(this_week.week[day].day)
                                    if shift.__class__.__name__ in [preferred_shift.__class__.__name__ for preferred_shift in employee.preferences[preference_day_index].shifts]:
                                        print(f"{employee.name} works shift {shift.__class__.__name__} (requested).")
                                        break
                                    else:
                                        print(
                                            f"{employee.name} works shift {shift.__class__.__name__} (not requested).")
                                        break
                                else:
                                    print(f"{employee.name} works shift {shift.__class__.__name__} (not requested).")
                                    break

                print()
                for name, shifts_this_week in number_of_shifts_this_week.items():
                    print(f"{name} got {shifts_this_week} shifts")

                print()
                print()
                count += 1
        else:
            print("No optimal solution found !")



def create_employee_list() -> List[Employee]:
    noa_sunday = DayPreferencesModel("Sunday", [EveningShift()])
    noa_monday = DayPreferencesModel("Monday", [MorningShift(), EveningShift()])
    noa_wednesday = DayPreferencesModel("Wednesday", [EveningShift()])
    noa_thursday = DayPreferencesModel("Thursday", [EveningShift()])
    noa_friday = DayPreferencesModel("Friday", [WeekendMorningShift(), WeekendMorningBackupShift(), EveningShift()])
    noa_saturday = DayPreferencesModel("Saturday", [WeekendMorningShift(), WeekendMorningBackupShift(), EveningShift()])

    chepo_sunday = DayPreferencesModel("Sunday", [EveningShift(), ClosingShift()])
    chepo_tuesday = DayPreferencesModel("Tuesday", [EveningShift(), ClosingShift()])
    chepo_wednesday = DayPreferencesModel("Wednesday", [EveningShift(), ClosingShift()])
    chepo_thursday = DayPreferencesModel("Thursday", [ClosingShift()])
    chepo_friday = DayPreferencesModel("Friday", [WeekendMorningShift(), WeekendMorningBackupShift(), EveningShift()])
    chepo_saturday = DayPreferencesModel("Saturday", [WeekendMorningShift()])

    beny_sunday = DayPreferencesModel("Sunday", [ClosingShift()])
    beny_tuesday = DayPreferencesModel("Tuesday", [ClosingShift()])
    beny_wednesday = DayPreferencesModel("Wednesday", [MorningShift(), EveningShift(), ClosingShift()])
    beny_thursday = DayPreferencesModel("Thursday", [ThursdayBackupShift(), ClosingShift()])
    beny_friday = DayPreferencesModel("Friday", [WeekendMorningShift()])
    beny_saturday = DayPreferencesModel("Saturday", [EveningShift(), ClosingShift()])

    misha_monday = DayPreferencesModel("Monday", [EveningShift(), ClosingShift()])
    misha_tuesday = DayPreferencesModel("Tuesday", [EveningShift(), ClosingShift()])
    misha_wednesday = DayPreferencesModel("Wednesday", [EveningShift(), ClosingShift()])
    misha_thursday = DayPreferencesModel("Thursday", [ThursdayBackupShift(), ClosingShift()])
    misha_friday = DayPreferencesModel("Friday", [WeekendMorningBackupShift(), EveningShift(), ClosingShift()])
    misha_saturday = DayPreferencesModel("Saturday", [WeekendMorningBackupShift(), EveningShift(), ClosingShift()])

    dan_sunday = DayPreferencesModel("Sunday", [MorningShift(), EveningShift(), ClosingShift()])
    dan_monday = DayPreferencesModel("Monday", [MorningShift(), EveningShift(), ClosingShift()])
    dan_tuesday = DayPreferencesModel("Tuesday", [MorningShift(), EveningShift(), ClosingShift()])
    dan_friday = DayPreferencesModel("Friday", [MorningShift(), EveningShift(), ClosingShift()])
    dan_saturday = DayPreferencesModel("Saturday", [MorningShift(), EveningShift(), ClosingShift()])

    noa_preferences = [noa_sunday, noa_monday, noa_wednesday, noa_thursday, noa_friday, noa_saturday]
    chepo_preferences = [chepo_sunday, chepo_tuesday, chepo_wednesday, chepo_thursday, chepo_friday, chepo_saturday]
    beny_preferences = [beny_sunday, beny_tuesday, beny_wednesday, beny_thursday, beny_friday, beny_saturday]
    misha_preferences = [misha_monday, misha_tuesday, misha_wednesday, misha_thursday, misha_friday, misha_saturday]
    dan_preferences = [dan_sunday, dan_monday, dan_tuesday, dan_friday, dan_saturday]

    noa = Employee("Noa", noa_preferences, 5, False, [], False)
    chepo = Employee("Chepo", chepo_preferences, 4, False,[], False)
    beny = Employee("Beny", beny_preferences, 4, False, [DayModel("Thursday")], True)
    misha = Employee("Misha", misha_preferences, 2, True, [], False)
    # dan = Employee("Dan", dan_preferences, 3, True, [], False)

    return Employee.instances


if __name__ == "__main__":

    days = [DayScheduleModel("Sunday", [MorningShift(), EveningShift(), ClosingShift()]),
            DayScheduleModel("Monday", [MorningShift(), EveningShift(), ClosingShift()]),
            DayScheduleModel("Tuesday", [MorningShift(), EveningShift(), ClosingShift()]),
            DayScheduleModel("Wednesday", [MorningShift(), EveningShift(), ClosingShift()]),
            DayScheduleModel("Thursday", [EveningShift(), ThursdayBackupShift(), ClosingShift()]),
            DayScheduleModel("Friday", [WeekendMorningShift(), WeekendMorningBackupShift(), EveningShift(), ClosingShift()]),
            DayScheduleModel("Saturday", [WeekendMorningShift(), WeekendMorningBackupShift(), EveningShift(), ClosingShift()])]

    create_schedule(create_employee_list(), WorkersWeekScheduleModel(days))

