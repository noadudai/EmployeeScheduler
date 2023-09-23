from typing import List

from ortools.sat.python import cp_model

from Models.Employee_model import Employee


def create_employees_preferences(names, preferences, priorities, is_new, day_offs, requests):
    for i in range(len(names)):
        Employee(names[i], preferences[i], priorities[i], is_new[i], day_offs[i], requests[i])

    return Employee.instances


# A function that will add constraints based on the day and the employees in that day, preventing 2 new employees
# from being in the same shift together (2 and 3 on Sun-Wed, 1 and 2 on Fri-San and 3 and 4 on Fri-Sat).
def add_constraint_of_no_2_employees(shift1: int, shift2: int, day: int, shifts: dict,
                                     all_employees: List[Employee], model):
    new_employee_1 = sum(shifts[(employee, day, shift1)] for employee in range(len(all_employees))
                         if all_employees[employee].is_new)
    new_employee_2 = sum(shifts[(employee, day, shift2)] for employee in range(len(all_employees))
                         if all_employees[employee].is_new)

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


def create_schedule(employees: List[Employee]):
    # Data for the program
    shifts_per_day = [3, 3, 3, 3, 4, 4, 4]
    max_shifts_a_week = 6
    number_of_days = 7

    all_employees = range(len(employees))
    all_shifts = range(max(shifts_per_day))
    all_days = range(number_of_days)

    # The 'Constraint Programming' model
    model = cp_model.CpModel()

    # Adding variables and constraints to the model:

    # A dictionary that will hold employees as a (employee, day, shift)  as a key, snd a
    # boolean value of 1 or 0 if that employee is working on that day on that shift.
    shifts = {}
    for employee in all_employees:
        for day in all_days:
            for shift in all_shifts[:shifts_per_day[day]]:
                shifts[(employee, day, shift)] = model.NewBoolVar(f"shift_employee{employee}_day{day}_shift{shift}")

    # A constraint that there will be only one employee in each shift per day
    for day in all_days:
        for shift in all_shifts[:shifts_per_day[day]]:
            # shifts[(0, 0, 1)] = 0/1
            # shifts[(1, 0, 1)] = 0/1
            # .
            # .
            # .
            model.AddExactlyOne(shifts[(employee, day, shift)] for employee in all_employees)

    # A constraint that each employee works at most one shift per day
    for employee in all_employees:
        for day in all_days:
            # shifts[(0, 0, 1)] = 0/1
            # shifts[(0, 0, 2)] = 0/1
            # .
            # .
            # .
            model.AddAtMostOne(shifts[(employee, day, shift)] for shift in all_shifts[:shifts_per_day[day]])

    # A constraint that ensures that on a given day, there are no more than two new employees on
    # shifts 1 and 2 (or 2 and 3 on Fri-Sat).
    for day in all_days:
        if day in range(0, 4):  # Sun-Wed
            add_constraint_of_no_2_employees(1, 2, day, shifts, employees, model)

        elif day in [4, 5, 6]:  # Fri-Sat
            add_constraint_of_no_2_employees(0, 1, day, shifts, employees, model)
            add_constraint_of_no_2_employees(2, 3, day, shifts, employees, model)

    # A constraint that ensures that each employee does not work more than 6 days in a week
    total_shifts_worked = {}
    for employee in all_employees:
        total_shifts_worked[employee] = sum(shifts[(employee, day, shift)] for day in all_days for shift
                                            in all_shifts[:shifts_per_day[day]])

    for employee in all_employees:
        model.Add(total_shifts_worked[employee] <= max_shifts_a_week)

    for employee in all_employees:
        for day in all_days:
            if day > 3 and day in employees[employee].days_off:
                for shift in all_shifts[:shifts_per_day[day]]:
                    model.Add(shifts[(employee, day, shift)] == 0).OnlyEnforceIf(employees[employee].day_off_requested)

    objective = sum(
        employees[employee].priority * employees[employee].preferences[day][shift] * shifts[(employee, day, shift)]
        for employee in all_employees
        for day in all_days
        for shift in all_shifts[:shifts_per_day[day]]
    )

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
                (employee, day, shift) for day in all_days for employee in all_employees for shift in
                all_shifts[:shifts_per_day[day]]
                if solver.Value(shifts[(employee, day, shift)])
            )

            if solution_identifier not in previous_solution:
                previous_solution.add(solution_identifier)

                print(f"Solution:{count}")
                for day in all_days:
                    print("Day", day)
                    for employee in all_employees:
                        for shift in all_shifts[:shifts_per_day[day]]:
                            if solver.Value(shifts[(employee, day, shift)]):

                                number_of_shifts_this_week[employees[employee].name] += 1

                                if employees[employee].preferences[day][shift] == 1:
                                    print(f"{employees[employee].name} works shift {shift} (requested).")
                                else:
                                    print(f"{employees[employee].name} works shift {shift} (not requested).")

                print()
                for name, shifts_this_week in number_of_shifts_this_week.items():
                    print(f"{name} got {shifts_this_week} shifts")

                print()
                print()
                count += 1
        else:
            print("No optimal solution found !")


if __name__ == "__main__":
    # Data for the scheduler:

    employees_names = ['Noa', 'Chepo', 'diamond', 'Alona', 'Beny', 'Misha', 'Liran']
    employees_priority = [5, 4, 2, 3, 4, 3, 3]
    employees_preferences = [
        [[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0]],
        [[1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 1, 1], [0, 0, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[1, 1, 1], [1, 1, 1], [1, 1, 1], [0, 0, 0], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 0], [0, 0, 0], [0, 0, 0], [1, 1, 1], [0, 0, 1, 1], [1, 0, 0, 0], [0, 0, 1, 1]],
        [[0, 0, 0], [0, 1, 1], [0, 1, 1], [0, 1, 1], [0, 0, 1, 1], [0, 1, 1, 1], [0, 1, 1, 1]],
        [[0, 0, 0], [0, 0, 0], [1, 1, 1], [1, 1, 1], [0, 0, 0, 0], [1, 1, 1, 1], [1, 1, 1, 1]]
    ]
    employees_days_off = [
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ]

    employees_days_off_request = [
        [0],
        [0],
        [0],
        [0],
        [0],
        [0],
        [0]
    ]

    employees_status = [False, False, False, True, True, True, True]

    create_schedule(create_employees_preferences(employees_names, employees_preferences,
                                                 employees_priority, employees_status, employees_days_off, employees_days_off_request))
