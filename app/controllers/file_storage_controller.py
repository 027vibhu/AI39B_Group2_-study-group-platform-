import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app.controllers.base_controller import BaseController
from app.models.file_storage import (
    upload_file, get_file_by_id, get_files_in_folder, 
    get_files_in_room, delete_file, move_file_to_folder, update_file
)
from app.models.folder import get_folder_by_id


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip'}
UPLOAD_FOLDER = 'app/static/uploads/files'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class FileStorageController(BaseController):
    def __init__(self):
        super().__init__()
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def upload_file_handler(self):
        """Upload a file to a folder"""
        try:
            if 'file' not in request.files:
                return jsonify({
                    "success": False,
                    "message": "No file provided"
                }), 400

            file = request.files['file']
            folder_id = request.form.get('folder_id')
            room_id = request.form.get('room_id')
            uploader_id = request.form.get('uploader_id')
            description = request.form.get('description')

            if not all([file, folder_id, room_id, uploader_id]):
                return jsonify({
                    "success": False,
                    "message": "file, folder_id, room_id, and uploader_id are required"
                }), 400

            if file.filename == '':
                return jsonify({
                    "success": False,
                    "message": "No file selected"
                }), 400

            if not allowed_file(file.filename):
                return jsonify({
                    "success": False,
                    "message": "File type not allowed"
                }), 400

            # Check folder exists
            folder = get_folder_by_id(folder_id)
            if not folder:
                return jsonify({
                    "success": False,
                    "message": "Folder not found"
                }), 404

            # Save file with secure name
            original_filename = secure_filename(file.filename)
            filename = f"{uploader_id}_{folder_id}_{original_filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # Get file size and type
            file_size = os.path.getsize(file_path)
            file_type = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'unknown'

            # Save to database
            result = upload_file(
                filename=filename,
                original_filename=original_filename,
                folder_id=int(folder_id),
                room_id=int(room_id),
                uploader_id=int(uploader_id),
                file_size=file_size,
                file_type=file_type,
                file_path=file_path,
                description=description
            )

            return jsonify({
                "success": True,
                "message": "File uploaded successfully",
                "file_id": result,
                "filename": original_filename
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def get_file_handler(self):
        """Get file details by ID"""
        data = request.get_json() or {}
        file_id = data.get("file_id")

        if not file_id:
            return jsonify({
                "success": False,
                "message": "file_id is required"
            }), 400

        try:
            file = get_file_by_id(file_id)
            if not file:
                return jsonify({
                    "success": False,
                    "message": "File not found"
                }), 404

            return jsonify({
                "success": True,
                "file": file
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def get_folder_files_handler(self):
        """Get all files in a folder"""
        data = request.get_json() or {}
        folder_id = data.get("folder_id")

        if not folder_id:
            return jsonify({
                "success": False,
                "message": "folder_id is required"
            }), 400

        try:
            files = get_files_in_folder(folder_id)
            return jsonify({
                "success": True,
                "files": files,
                "count": len(files)
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def get_room_files_handler(self):
        """Get all files in a room"""
        data = request.get_json() or {}
        room_id = data.get("room_id")

        if not room_id:
            return jsonify({
                "success": False,
                "message": "room_id is required"
            }), 400

        try:
            files = get_files_in_room(room_id)
            return jsonify({
                "success": True,
                "files": files,
                "count": len(files)
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def update_file_handler(self):
        """Update file details"""
        data = request.get_json() or {}
        file_id = data.get("file_id")
        description = data.get("description")

        if not file_id:
            return jsonify({
                "success": False,
                "message": "file_id is required"
            }), 400

        try:
            update_file(file_id, description=description)
            return jsonify({
                "success": True,
                "message": "File updated successfully"
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def delete_file_handler(self):
        """Delete a file"""
        data = request.get_json() or {}
        file_id = data.get("file_id")

        if not file_id:
            return jsonify({
                "success": False,
                "message": "file_id is required"
            }), 400

        try:
            file = get_file_by_id(file_id)
            if not file:
                return jsonify({
                    "success": False,
                    "message": "File not found"
                }), 404

            # Delete physical file
            if os.path.exists(file.get('file_path')):
                os.remove(file.get('file_path'))

            # Delete from database
            delete_file(file_id)
            return jsonify({
                "success": True,
                "message": "File deleted successfully"
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def move_file_handler(self):
        """Move file to another folder"""
        data = request.get_json() or {}
        file_id = data.get("file_id")
        new_folder_id = data.get("new_folder_id")

        if not file_id or not new_folder_id:
            return jsonify({
                "success": False,
                "message": "file_id and new_folder_id are required"
            }), 400

        try:
            file = get_file_by_id(file_id)
            if not file:
                return jsonify({
                    "success": False,
                    "message": "File not found"
                }), 404

            folder = get_folder_by_id(new_folder_id)
            if not folder:
                return jsonify({
                    "success": False,
                    "message": "Target folder not found"
                }), 404

            move_file_to_folder(file_id, new_folder_id)
            return jsonify({
                "success": True,
                "message": "File moved successfully"
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500
