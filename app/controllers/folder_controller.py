from flask import request, jsonify
from app.controllers.base_controller import BaseController
from app.models.folder import (
    create_folder, get_folder_by_id, get_folders_in_room, 
    get_folder_contents, update_folder, delete_folder, get_folder_path
)
from app.models.file_storage import (
    get_files_in_folder, get_folder_file_count, get_total_folder_size
)


class FolderController(BaseController):
    def __init__(self):
        super().__init__()

    def create_folder_handler(self):
        """Create a new folder"""
        data = request.get_json() or {}
        
        name = data.get("name")
        room_id = data.get("room_id")
        owner_id = data.get("owner_id")
        parent_folder_id = data.get("parent_folder_id")
        description = data.get("description")

        if not name or not room_id or not owner_id:
            return jsonify({
                "success": False, 
                "message": "name, room_id, and owner_id are required"
            }), 400

        try:
            result = create_folder(name, room_id, owner_id, parent_folder_id, description)
            return jsonify({
                "success": True,
                "message": "Folder created successfully",
                "folder_id": result
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def get_folder_handler(self):
        """Get folder details by ID"""
        data = request.get_json() or {}
        folder_id = data.get("folder_id")

        if not folder_id:
            return jsonify({
                "success": False,
                "message": "folder_id is required"
            }), 400

        try:
            folder = get_folder_by_id(folder_id)
            if not folder:
                return jsonify({
                    "success": False,
                    "message": "Folder not found"
                }), 404

            # Get contents
            subfolders = get_folder_contents(folder_id)
            files = get_files_in_folder(folder_id)
            file_count = get_folder_file_count(folder_id)
            total_size = get_total_folder_size(folder_id)

            return jsonify({
                "success": True,
                "folder": folder,
                "subfolders": subfolders,
                "files": files,
                "file_count": file_count,
                "total_size": total_size
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def get_room_folders_handler(self):
        """Get all root folders in a room"""
        data = request.get_json() or {}
        room_id = data.get("room_id")
        parent_folder_id = data.get("parent_folder_id")

        if not room_id:
            return jsonify({
                "success": False,
                "message": "room_id is required"
            }), 400

        try:
            folders = get_folders_in_room(room_id, parent_folder_id)
            return jsonify({
                "success": True,
                "folders": folders
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def update_folder_handler(self):
        """Update folder details"""
        data = request.get_json() or {}
        folder_id = data.get("folder_id")
        name = data.get("name")
        description = data.get("description")

        if not folder_id:
            return jsonify({
                "success": False,
                "message": "folder_id is required"
            }), 400

        try:
            result = update_folder(folder_id, name, description)
            return jsonify({
                "success": True,
                "message": "Folder updated successfully"
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def delete_folder_handler(self):
        """Delete a folder"""
        data = request.get_json() or {}
        folder_id = data.get("folder_id")

        if not folder_id:
            return jsonify({
                "success": False,
                "message": "folder_id is required"
            }), 400

        try:
            delete_folder(folder_id)
            return jsonify({
                "success": True,
                "message": "Folder deleted successfully"
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500

    def get_folder_path_handler(self):
        """Get the full path of a folder"""
        data = request.get_json() or {}
        folder_id = data.get("folder_id")

        if not folder_id:
            return jsonify({
                "success": False,
                "message": "folder_id is required"
            }), 400

        try:
            path = get_folder_path(folder_id)
            return jsonify({
                "success": True,
                "path": path
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": str(e)
            }), 500
