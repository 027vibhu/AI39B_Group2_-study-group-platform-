"""Unit tests for StudyHourController (StudyHour patched; stats aggregation)."""

import unittest
from datetime import date, timedelta
from unittest.mock import patch

from flask import session

from tests.support import make_controller_app


class StudyHourTestBase(unittest.TestCase):
    def setUp(self):
        self.app = make_controller_app()
        # Patch StudyHour -> neutralise __init__ ensure_table_exists().
        self.patcher = patch('app.controllers.study_hour_controller.StudyHour')
        self.StudyHour = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.model = self.StudyHour.return_value
        from app.controllers.study_hour_controller import StudyHourController
        self.controller = StudyHourController()


class TestCreateSession(StudyHourTestBase):
    def test_requires_login(self):
        with self.app.test_request_context(method='POST'):
            response = self.controller.create_session()
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_invalid_duration_flashes(self):
        with self.app.test_request_context(method='POST', data={'duration_minutes': 'abc'}):
            session['user_id'] = 1
            response = self.controller.create_session()
        self.assertEqual(response.status_code, 302)
        self.model.record.assert_not_called()

    def test_records_session(self):
        self.model.record.return_value = 1
        with self.app.test_request_context(method='POST',
                                           data={'session_date': '2026-06-01', 'duration_minutes': '90'}):
            session['user_id'] = 1
            response = self.controller.create_session()
        self.assertEqual(response.status_code, 302)
        self.model.record.assert_called_once()
        # duration converted to int
        self.assertEqual(self.model.record.call_args.args[2], 90)


class TestWidgetStats(StudyHourTestBase):
    def test_empty_sessions(self):
        self.model.find_for_user.return_value = []
        stats = self.controller.get_widget_stats(1)
        self.assertEqual(stats['total_hours'], 0)
        self.assertEqual(stats['streak'], 0)
        self.assertEqual(stats['study_days'], [])

    def test_streak_and_totals(self):
        today = date.today()
        self.model.find_for_user.return_value = [
            {'session_date': today, 'duration_minutes': 60},
            {'session_date': today - timedelta(days=1), 'duration_minutes': 120},
        ]
        stats = self.controller.get_widget_stats(1)
        self.assertEqual(stats['total_hours'], 3.0)
        self.assertEqual(stats['streak'], 2)
        self.assertEqual(stats['days_logged'], 2)
        self.assertEqual(stats['best_day']['hours'], 2.0)


if __name__ == '__main__':
    unittest.main()
