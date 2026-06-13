from datetime import datetime

from flask import request, flash, jsonify
from app.controllers.base_controller import BaseController
from app.models.study_hour import StudyHour


class StudyHourController(BaseController):
    def __init__(self):
        # Use the class helper to ensure table exists on controller init
        StudyHour.ensure_table_exists()
        self.model = StudyHour()

    def list_sessions(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        sessions = self.model.find_for_user(user_id)
        streaks = self.model.get_study_streaks(user_id)
        return self.render('study_hours/index.html', sessions=sessions, streaks=streaks)

    def new_session_form(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        return self.render('study_hours/new.html')

    def create_session(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.redirect('auth.login')

        # Expected form fields: session_date (YYYY-MM-DD), duration_minutes, notes
        session_date = (request.form.get('session_date') or '').strip()
        duration = (request.form.get('duration_minutes') or '').strip()
        notes = (request.form.get('notes') or '').strip() or None

        # Basic validation
        try:
            parsed_date = datetime.strptime(session_date, '%Y-%m-%d').date()
        except Exception:
            flash('Invalid session date. Use YYYY-MM-DD.', 'error')
            return self.redirect('home.dashboard')

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

    def get_streaks(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return jsonify({'error': 'Authentication required.'}), 401

        streaks = self.model.get_study_streaks(user_id)
        return jsonify({
            'status': 'success',
            'current_streak': streaks.get('current_streak', 0),
            'longest_streak': streaks.get('longest_streak', 0),
        })
