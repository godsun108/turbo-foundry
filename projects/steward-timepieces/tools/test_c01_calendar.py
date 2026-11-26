"""Unit tests for STEWARD C-01 calendar logic."""
import unittest

from c01_calendar import (
    advance_one_day, advance_days, validate_calendar_state,
    correct_date, correct_weekday, date_wheel_position,
    calendar_load_comparison,
)


class CalendarStateTests(unittest.TestCase):
    def test_state_validation(self):
        self.assertEqual(validate_calendar_state(28, 2, 28),
                         {"date": 28, "weekday": 2, "month_length": 28})

    def test_invalid_date_for_month(self):
        with self.assertRaises(ValueError):
            validate_calendar_state(31, 0, 30)

    def test_month_end_rollover(self):
        self.assertEqual(advance_one_day(30, 4, 30),
                         {"date": 1, "weekday": 5,
                          "month_rollover": True,
                          "manual_correction_required": False})

    def test_normal_day_advance(self):
        self.assertEqual(advance_one_day(12, 6, 31)["date"], 13)

    def test_weekday_wraps_after_seven(self):
        self.assertEqual(advance_one_day(1, 6, 31)["weekday"], 0)

    def test_multi_day_advance(self):
        self.assertEqual(advance_days(29, 1, 31, 3),
                         {"date": 1, "weekday": 4})

    def test_zero_day_advance(self):
        self.assertEqual(advance_days(15, 3, 31, 0),
                         {"date": 15, "weekday": 3})


class CorrectionTests(unittest.TestCase):
    def test_independent_date_correction(self):
        self.assertEqual(correct_date(30, 30), 30)

    def test_date_correction_rejects_invalid_day(self):
        with self.assertRaises(ValueError):
            correct_date(31, 30)

    def test_independent_weekday_correction(self):
        self.assertEqual(correct_weekday(6), 6)

    def test_invalid_weekday(self):
        with self.assertRaises(ValueError):
            correct_weekday(7)

    def test_date_wheel_position(self):
        self.assertEqual(date_wheel_position(1), 0)
        self.assertEqual(date_wheel_position(31), 30)


class CalendarLoadTests(unittest.TestCase):
    def test_matched_interval_load_delta(self):
        result = calendar_load_comparison(0.010, 0.014, 60, 60)
        self.assertAlmostEqual(result["incremental_energy_j"], 0.004)
        self.assertAlmostEqual(result["incremental_average_power_w"],
                               0.004 / 60)

    def test_mismatched_intervals_rejected(self):
        with self.assertRaises(ValueError):
            calendar_load_comparison(1, 2, 60, 61)


if __name__ == "__main__":
    unittest.main()
