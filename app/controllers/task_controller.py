from flask import request, jsonify, flash
from app.controllers.base_controller import BaseController
from app.models.task import Task


class TaskController(BaseController):
    """Handles the dashboard to-do list widget."""

    def __init__(self):
        Task.ensure_table_exists()

    def _wants_json(self):
        return (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            or request.is_json
            or request.accept_mimetypes.best == 'application/json'
        )

    def _serialize(self, task):
        """Shape a task row into JSON-friendly fields for the schedule board."""
        due = task.get('due_date')
        if hasattr(due, 'isoformat'):
            due = due.isoformat()
        return {
            'id': task.get('id'),
            'title': task.get('title'),
            'description': task.get('description') or '',
            'status': task.get('status') or 'todo',
            'priority': task.get('priority') or 'medium',
            'due_date': due or '',
            'is_done': task.get('is_done', 0),
        }

    def list_for_user(self, user_id):
        if not user_id:
            return []
        return Task.find_for_user(user_id)

    def create_task(self):
        user_id = self.get_current_user_id()
        if not user_id:
            if self._wants_json():
                return jsonify({'status': 'error', 'message': 'Login required.'}), 401
            return self.redirect('auth.login')

        title = (request.form.get('title') or '').strip()
        if not title:
            if self._wants_json():
                return jsonify({'status': 'error', 'message': 'Task cannot be empty.'}), 400
            flash('Task cannot be empty.', 'warning')
            return self.redirect('home.schedule_page')

        title = title[:255]
        status = (request.form.get('status') or 'todo').strip()
        priority = (request.form.get('priority') or 'medium').strip()
        due_date = (request.form.get('due_date') or '').strip()
        description = (request.form.get('description') or '').strip()
        new_id = Task.create(user_id, title, status=status,
                             due_date=due_date, priority=priority,
                             description=description)

        if self._wants_json():
            return jsonify({
                'status': 'success',
                'task': self._serialize({
                    'id': new_id,
                    'title': title,
                    'description': description,
                    'status': status,
                    'priority': priority,
                    'due_date': due_date,
                    'is_done': 1 if status == 'done' else 0,
                }),
            }), 201

        return self.redirect('home.schedule')

    def update_task(self, task_id):
        user_id = self.get_current_user_id()
        if not user_id:
            if self._wants_json():
                return jsonify({'status': 'error', 'message': 'Login required.'}), 401
            return self.redirect('auth.login')

        # Only pass through fields that were actually supplied so a status-only
        # move doesn't wipe the title/due date (and vice versa).
        status = request.form.get('status', None)
        due_date = request.form.get('due_date', None)
        priority = request.form.get('priority', None)
        title = request.form.get('title', None)
        description = request.form.get('description', None)
        if title is not None:
            title = title.strip()
            if not title:  # don't allow blanking the title via edit
                title = None

        updated = Task.update(task_id, user_id, status=status,
                              due_date=due_date, priority=priority,
                              title=title, description=description)
        if not updated:
            if self._wants_json():
                return jsonify({'status': 'error', 'message': 'Task not found.'}), 404
            return self.redirect('home.schedule_page')

        if self._wants_json():
            return jsonify({'status': 'success', 'task': self._serialize(updated)}), 200

        return self.redirect('home.schedule')

    def toggle_task(self, task_id):
        user_id = self.get_current_user_id()
        if not user_id:
            if self._wants_json():
                return jsonify({'status': 'error', 'message': 'Login required.'}), 401
            return self.redirect('auth.login')

        is_done = Task.toggle(task_id, user_id)
        if is_done is None:
            if self._wants_json():
                return jsonify({'status': 'error', 'message': 'Task not found.'}), 404
            return self.redirect('home.schedule_page')

        if self._wants_json():
            return jsonify({'status': 'success', 'is_done': is_done}), 200

        return self.redirect('home.dashboard')

    def delete_task(self, task_id):
        user_id = self.get_current_user_id()
        if not user_id:
            if self._wants_json():
                return jsonify({'status': 'error', 'message': 'Login required.'}), 401
            return self.redirect('auth.login')

        Task.delete(task_id, user_id)

        if self._wants_json():
            return jsonify({'status': 'success'}), 200

        return self.redirect('home.dashboard')
