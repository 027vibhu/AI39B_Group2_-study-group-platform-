from flask import Blueprint, jsonify, request
from app.controllers.exam_countdown_controller import ExamCountdownController


class ExamCountdownRoutes:
    def __init__(self):
        self.bp = Blueprint('exam_countdown', __name__)

    def register(self):
        self.bp.route('/exams', methods=['GET'])(self.list_exams)
        self.bp.route('/exams', methods=['POST'])(self.create_exam)
        return self.bp

    def list_exams(self):
        controller = ExamCountdownController()
        try:
            exams = controller.list_exams()
            return jsonify({'status': 'success', 'exams': exams}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    def create_exam(self):
        controller = ExamCountdownController()
        data = request.get_json() or request.form
        title = data.get('title')
        exam_datetime = data.get('exam_datetime')
        notes = data.get('notes', '')
        color = data.get('color', None)

        if not title or not exam_datetime:
            return jsonify({'status': 'error', 'message': 'title and exam_datetime are required'}), 400

        try:
            new_id = controller.create_exam(title, exam_datetime, notes, color=color, user_id=None)
            return jsonify({'status': 'success', 'id': new_id}), 201
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500


# Expose blueprint for app registration
exam_bp = ExamCountdownRoutes().register()
