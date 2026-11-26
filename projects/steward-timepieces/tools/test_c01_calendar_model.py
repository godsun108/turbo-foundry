import unittest

from c01_calendar_model import (
    CalendarState, calendar_event_energy_per_day, correct_date,
    correct_weekday, daily_changeover, month_end_correction_steps,
)


class CalendarModelTests(unittest.TestCase):
    def test_daily_changeover_advances_both_indications(self):
        result = daily_changeover(CalendarState(0, 14))
        self.assertEqual(result, CalendarState(1, 15))

    def test_weekday_wraps_after_sunday(self):
        self.assertEqual(daily_changeover(CalendarState(6, 31)),
                         CalendarState(0, 1))

    def test_date_wraps_from_31_to_1(self):
        self.assertEqual(daily_changeover(CalendarState(2, 31)).date, 1)

    def test_weekday_quick_set_is_independent(self):
        result = correct_weekday(CalendarState(2, 17), 1, True)
        self.assertEqual(result, CalendarState(3, 17))

    def test_date_quick_set_is_independent_and_wraps(self):
        self.assertEqual(correct_date(CalendarState(4, 31), 1, True),
                         CalendarState(4, 1))
        self.assertEqual(correct_date(CalendarState(4, 1), -1, True),
                         CalendarState(4, 31))

    def test_correction_is_blocked_without_verified_permission(self):
        with self.assertRaises(ValueError):
            correct_date(CalendarState(0, 10), 1, False)
        with self.assertRaises(ValueError):
            correct_weekday(CalendarState(0, 10), -1, False)

    def test_invalid_direction_rejected(self):
        with self.assertRaises(ValueError):
            correct_date(CalendarState(0, 10), 0, True)

    def test_month_end_manual_correction_steps(self):
        self.assertEqual(month_end_correction_steps(31), 0)
        self.assertEqual(month_end_correction_steps(30), 1)
        self.assertEqual(month_end_correction_steps(29), 2)
        self.assertEqual(month_end_correction_steps(28), 3)

    def test_calendar_event_energy_documents_coincidence(self):
        self.assertEqual(calendar_event_energy_per_day(0.002, 0.0), 0.002)
        self.assertEqual(calendar_event_energy_per_day(0.001, 0.0005, False), 0.0015)
        with self.assertRaises(ValueError):
            calendar_event_energy_per_day(0.001, 0.0005, True)

    def test_invalid_calendar_state_rejected(self):
        with self.assertRaises(ValueError):
            CalendarState(7, 10)
        with self.assertRaises(ValueError):
            CalendarState(0, 32)


if __name__ == "__main__":
    unittest.main()
