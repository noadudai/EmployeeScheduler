from typing import List


def hi(day_off: List[int]):
    day_offs = [0, 0, 0, 0, 0, 0, 0]
    # days_off = [1 for i in range(7) if i in day_off else 0]
    for i in range(len(day_offs)):
        if i in day_off:
            day_offs[i] = 1

    for i in day_offs:
        print(i)


if __name__ == '__main__':
    days = [1, 3]
    hi(days)
