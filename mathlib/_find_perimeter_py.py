"""Pure-Python fallback for the Cython marching-squares perimeter calculator.

This is functionally equivalent to _find_perimeter_cy._get_perimeter but
runs significantly slower since it lacks Cython optimizations. It is used
automatically when the Cython extension has not been compiled.
"""
import numpy as np
from math import sqrt


def _hypot(x, y):
    return sqrt(x * x + y * y)


def _get_fraction(from_value, to_value, level):
    if to_value == from_value:
        return 0.0
    return (level - from_value) / (to_value - from_value)


def _get_perimeter(array, level, vertex_connect_high, returning_contours):
    """Marching-squares perimeter / contour extraction (pure-Python)."""
    # Convert masked arrays to regular ndarrays (masked values become fill_value)
    # The Cython version uses typed memoryviews which strip mask info automatically.
    if hasattr(array, 'filled'):
        array = array.filled(0.0)
    elif not isinstance(array, np.ndarray):
        array = np.asarray(array, dtype=np.float64)

    segments = []
    perimeter = 0.0

    rows, cols = array.shape

    for r0 in range(3, rows - 4):
        for c0 in range(3, cols - 4):
            r1 = r0 + 1
            c1 = c0 + 1

            ul = array[r0, c0]
            ur = array[r0, c1]
            ll = array[r1, c0]
            lr = array[r1, c1]

            square_case = (
                int(ul > level)
                + int(ur > level) * 2
                + int(ll > level) * 4
                + int(lr > level) * 8
            )

            if square_case in (0, 15):
                continue

            if not returning_contours:
                dist = _hypot(
                    r0 + 0.5 - rows / 2.0,
                    c0 + 0.5 - cols / 2.0,
                )
                if dist > rows / 2.0 - 3:
                    continue

            top = _get_fraction(ul, ur, level)
            bottom = _get_fraction(ll, lr, level)
            left = _get_fraction(ll, ul, level)
            right = _get_fraction(lr, ur, level)

            if returning_contours:
                top_tuple = (r0, c0 + _get_fraction(ul, ur, level))
                bottom_tuple = (r1, c0 + _get_fraction(ll, lr, level))
                left_tuple = (r0 + _get_fraction(ul, ll, level), c0)
                right_tuple = (r0 + _get_fraction(ur, lr, level), c1)

            add_var = 0.0

            if square_case == 1:
                if returning_contours:
                    segments.append((top_tuple, left_tuple))
                add_var = _hypot(top, 1 - left)
            elif square_case == 2:
                if returning_contours:
                    segments.append((right_tuple, top_tuple))
                add_var = _hypot(1 - top, 1 - right)
            elif square_case == 3:
                if returning_contours:
                    segments.append((right_tuple, left_tuple))
                add_var = _hypot(right - left, 1)
            elif square_case == 4:
                if returning_contours:
                    segments.append((left_tuple, bottom_tuple))
                add_var = _hypot(left, bottom)
            elif square_case == 5:
                if returning_contours:
                    segments.append((top_tuple, bottom_tuple))
                add_var = _hypot(top - bottom, 1)
            elif square_case == 6:
                if returning_contours:
                    if vertex_connect_high:
                        segments.append((left_tuple, top_tuple))
                        segments.append((right_tuple, bottom_tuple))
                    else:
                        segments.append((right_tuple, top_tuple))
                        segments.append((left_tuple, bottom_tuple))
                add_var = _hypot(1 - top, 1 - right) + _hypot(left, bottom)
            elif square_case == 7:
                if returning_contours:
                    segments.append((right_tuple, bottom_tuple))
                add_var = _hypot(1 - bottom, right)
            elif square_case == 8:
                if returning_contours:
                    segments.append((bottom_tuple, right_tuple))
                add_var = _hypot(1 - bottom, right)
            elif square_case == 9:
                if returning_contours:
                    if vertex_connect_high:
                        segments.append((top_tuple, right_tuple))
                        segments.append((bottom_tuple, left_tuple))
                    else:
                        segments.append((top_tuple, left_tuple))
                        segments.append((bottom_tuple, right_tuple))
                add_var = _hypot(top, 1 - left) + _hypot(1 - bottom, right)
            elif square_case == 10:
                if returning_contours:
                    segments.append((bottom_tuple, top_tuple))
                add_var = _hypot(top - bottom, 1)
            elif square_case == 11:
                if returning_contours:
                    segments.append((bottom_tuple, left_tuple))
                add_var = _hypot(left, bottom)
            elif square_case == 12:
                if returning_contours:
                    segments.append((left_tuple, right_tuple))
                add_var = _hypot(right - left, 1)
            elif square_case == 13:
                if returning_contours:
                    segments.append((top_tuple, right_tuple))
                add_var = _hypot(1 - top, 1 - right)
            elif square_case == 14:
                if returning_contours:
                    segments.append((left_tuple, top_tuple))
                add_var = _hypot(top, 1 - left)

            perimeter += add_var

    return (perimeter, segments)
