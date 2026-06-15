from datetime import datetime, date, timedelta
from flask import request, flash
from app.controllers.base_controller import BaseController
from app.models.study_hour import StudyHour


class StudyHourController(BaseController):
    def __init__(self):
        # Use the class helper to ensure table exists on controller init
        StudyHour.ensure_table_exists()
        self.model = StudyHour()

    def create_session(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        # Expected form fields: session_date (YYYY-MM-DD, optional), duration_minutes, notes
        session_date = (request.form.get('session_date') or '').strip()
        duration = (request.form.get('duration_minutes') or '').strip()
        notes = (request.form.get('notes') or '').strip() or None

        # Default to today when no date is supplied (widget logs "today").
        if session_date:
            try:
                parsed_date = datetime.strptime(session_date, '%Y-%m-%d').date()
            except Exception:
                flash('Invalid session date. Use YYYY-MM-DD.', 'error')
                return self.redirect('home.dashboard')
        else:
            parsed_date = date.today()

        try:
            duration_int = int(duration)
            if duration_int <= 0:
                raise ValueError()
        except Exception:
            flash('Duration must be a positive integer (minutes).', 'error')
            return self.redirect('home.dashboard')

        # Record the session using raw-SQL model
        new_id = self.model.record(user_id, parsed_date, duration_int, notes)
        if new_id:
            flash('Study session recorded.', 'success')
        else:
            flash('Failed to record study session.', 'error')

        return self.redirect('home.dashboard')

    def get_widget_stats(self, user_id):
        """Aggregate study-hours data for the dashboard widgets.

        Returns total hours, hours studied this week, the current streak, and a
        per-day breakdown (`study_days`). The Study Streak widget renders purely
        from `study_days`, so logging a session here keeps that widget in sync.
        """
        sessions = self.model.find_for_user(user_id, limit=500)

        # Calculate total hours
        total_minutes = sum(s.get('duration_minutes', 0) for s in sessions) if sessions else 0
        total_hours = round(total_minutes / 60, 1) if total_minutes else 0

        # Aggregate minutes per calendar day (normalise dates to date objects).
        per_day = {}
        for session in sessions or []:
            session_date = session['session_date']
            if isinstance(session_date, str):
                session_date = datetime.strptime(session_date, '%Y-%m-%d').date()
            per_day[session_date] = per_day.get(session_date, 0) + session.get('duration_minutes', 0)

        # Per-day breakdown the Study Streak widget renders from (oldest first).
        study_days = [
            {'date': d.isoformat(), 'minutes': minutes}
            for d, minutes in sorted(per_day.items())
        ]

        # Hours studied during the current week (Monday through Sunday).
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_minutes = sum(m for d, m in per_day.items() if week_start <= d <= week_end)
        weekly_hours = round(week_minutes / 60, 1) if week_minutes else 0

        # Current streak: consecutive days with a session ending today or yesterday.
        streak = 0
        if per_day:
            cursor = today if today in per_day else (today - timedelta(days=1))
            while cursor in per_day:
                streak += 1
                cursor -= timedelta(days=1)

        return {
            'total_hours': total_hours,
            'weekly_hours': weekly_hours,
            'streak': streak,
            'study_days': study_days,
            'recent_sessions': sessions[:10] if sessions else []
        }
