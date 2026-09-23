from typing import Generator

def iter_clockwise(data, start_index):
    """Begins iterating at the element at the start index, and loops around back to the element before the starting element."""
    n = len(data)
    for i in range(n):
        yield data[(start_index + i) % n]

def enumerate_clockwise(data, start_index):
    """Combines `enumerate` and `iter_clockwise`."""
    n = len(data)
    for i in range(n):
        index = (start_index + i) % n
        yield (index, data[index])
