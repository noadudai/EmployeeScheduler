from typing import List

from Models.Day_model import DayModel
from Models.Employee_model import Employee
from Models.Day_schedule_model import DayScheduleModel
from Models.Day_preferences_model import DayPreferencesModel
from Models.Shifts_model import *  # ClosingShift, MorningShift, EveningShift, WeekendMorningShift, WeekendMorningBackupShift, ThursdayBackupShift
from Models.Workers_week_schedule import WorkersWeekScheduleModel

from ortools.sat.python import cp_model


def create_schedule(employees: List[Employee]) -> WorkersWeekScheduleModel:
    # The last time I checked there were 7 days in a week (LOL😂).
    NUMBER_OF_DAYS_A_WEEK_KEY = 7
    this_week = WorkersWeekScheduleModel()

    # The length of the shifts list in each day, is the number of shifts in a day.
    shifts_per_day = [len(this_week.week[day].shifts) for day in range(NUMBER_OF_DAYS_A_WEEK_KEY)]

    # The max shifts for an employee in a week is 6 by law.
    max_shifts_in_a_week = 6

    number_of_days_in_a_week = NUMBER_OF_DAYS_A_WEEK_KEY

    all_employees = range(len(employees))
    all_days = range(number_of_days_in_a_week)

    # The 'Constraint Programming' model
    model = cp_model.CpModel()

    assert(shifts_per_day == [3, 3, 3, 3, 4, 4, 4])

    return this_week


if __name__ == "__main__":

    noa_sunday = DayPreferencesModel("Sunday", [EveningShift()])
    noa_monday = DayPreferencesModel("Monday", [EveningShift()])
    noa_wednesday = DayPreferencesModel("Wednesday", [EveningShift()])
    noa_thursday = DayPreferencesModel("Thursday", [EveningShift()])
    noa_friday = DayPreferencesModel("Friday", [EveningShift()])
    noa_saturday = DayPreferencesModel("Saturday", [EveningShift()])

    chepo_sunday = DayPreferencesModel("Sunday", [MorningShift()])
    chepo_wednesday = DayPreferencesModel("Wednesday", [EveningShift(), ClosingShift()])
    chepo_thursday = DayPreferencesModel("Thursday", [EveningShift(), ClosingShift()])

    beny_wednesday = DayPreferencesModel("Wednesday", [MorningShift(), EveningShift(), ClosingShift()])
    beny_thursday = DayPreferencesModel("Thursday", [ThursdayBackupShift(), ClosingShift()])
    beny_friday = DayPreferencesModel("Friday", [MorningShift()])
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
    dan_wednesday = DayPreferencesModel("Wednesday", [MorningShift(), EveningShift(), ClosingShift()])
    dan_thursday = DayPreferencesModel("Thursday", [MorningShift(), EveningShift(), ClosingShift()])
    dan_friday = DayPreferencesModel("Friday", [MorningShift(), EveningShift(), ClosingShift()])
    dan_saturday = DayPreferencesModel("Saturday", [MorningShift(), EveningShift(), ClosingShift()])

    noa_preferences = [noa_sunday, noa_monday, noa_wednesday, noa_thursday, noa_friday, noa_saturday]
    chepo_preferences = [chepo_sunday, chepo_thursday, chepo_wednesday]
    beny_preferences = [beny_wednesday, beny_thursday, beny_friday, beny_saturday]
    misha_preferences = [misha_monday, misha_tuesday, misha_wednesday, misha_thursday, misha_friday, misha_saturday]
    dan_preferences = [dan_sunday, dan_monday, dan_tuesday, dan_wednesday, dan_thursday, dan_friday, dan_saturday]

    noa = Employee("Noa", noa_preferences, 5, False, [], False)
    chepo = Employee("Chepo", chepo_preferences, 4, False, [DayModel("Monday"), DayModel("Tuesday"), DayModel("Friday"), DayModel("Saturday")], True)
    beny = Employee("Beny", beny_preferences, 3, False, [], False)
    misha = Employee("Misha", misha_preferences, 2, True, [], False)
    dan = Employee("Dan", dan_preferences, 3, True, [], False)

    this_week_schedule = create_schedule(Employee.instances)

