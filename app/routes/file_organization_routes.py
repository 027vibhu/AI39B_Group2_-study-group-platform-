from flask import Blueprint

from app.controllers.folder_controller import FolderController
from app.controllers.file_storage_controller import FileStorageController


class FileOrganizationRoutes:
    def __init__(self):
        self.bp = Blueprint("file_organization", __name__)
        self.folder_controller = FolderController()
        self.file_controller = FileStorageController()

    def register(self):
        # Folder routes
        self.bp.route("/folder/create", methods=["POST"])(self.create_folder)
        self.bp.route("/folder/<int:folder_id>", methods=["GET"])(self.get_folder)
        self.bp.route("/folder/room/<int:room_id>", methods=["GET"])(self.get_room_folders)
        self.bp.route("/folder/update", methods=["PUT"])(self.update_folder)
        self.bp.route("/folder/delete", methods=["DELETE"])(self.delete_folder)
        self.bp.route("/folder/path", methods=["POST"])(self.get_folder_path)

        # File routes
        self.bp.route("/file/upload", methods=["POST"])(self.upload_file)
        self.bp.route("/file/<int:file_id>", methods=["GET"])(self.get_file)
        self.bp.route("/file/folder/<int:folder_id>", methods=["GET"])(self.get_folder_files)
        self.bp.route("/file/room/<int:room_id>", methods=["GET"])(self.get_room_files)
        self.bp.route("/file/update", methods=["PUT"])(self.update_file)
        self.bp.route("/file/delete", methods=["DELETE"])(self.delete_file)
        self.bp.route("/file/move", methods=["POST"])(self.move_file)

        return self.bp

    # Folder endpoints
    def create_folder(self):
        return self.folder_controller.create_folder_handler()

    def get_folder(self, folder_id):
        from flask import request
        data = request.get_json() or {}
        data['folder_id'] = folder_id
        from flask import Request
        original_get_json = request.get_json
        request.get_json = lambda: data
        result = self.folder_controller.get_folder_handler()
        request.get_json = original_get_json
        return result

    def get_room_folders(self, room_id):
        from flask import request
        data = request.get_json() or {}
        data['room_id'] = room_id
        from flask import Request
        original_get_json = request.get_json
        request.get_json = lambda: data
        result = self.folder_controller.get_room_folders_handler()
        request.get_json = original_get_json
        return result

    def update_folder(self):
        return self.folder_controller.update_folder_handler()

    def delete_folder(self):
        return self.folder_controller.delete_folder_handler()

    def get_folder_path(self):
        return self.folder_controller.get_folder_path_handler()

    # File endpoints
    def upload_file(self):
        return self.file_controller.upload_file_handler()

    def get_file(self, file_id):
        from flask import request
        data = request.get_json() or {}
        data['file_id'] = file_id
        from flask import Request
        original_get_json = request.get_json
        request.get_json = lambda: data
        result = self.file_controller.get_file_handler()
        request.get_json = original_get_json
        return result

    def get_folder_files(self, folder_id):
        from flask import request
        data = request.get_json() or {}
        data['folder_id'] = folder_id
        from flask import Request
        original_get_json = request.get_json
        request.get_json = lambda: data
        result = self.file_controller.get_folder_files_handler()
        request.get_json = original_get_json
        return result

    def get_room_files(self, room_id):
        from flask import request
        data = request.get_json() or {}
        data['room_id'] = room_id
        from flask import Request
        original_get_json = request.get_json
        request.get_json = lambda: data
        result = self.file_controller.get_room_files_handler()
        request.get_json = original_get_json
        return result

    def update_file(self):
        return self.file_controller.update_file_handler()

    def delete_file(self):
        return self.file_controller.delete_file_handler()

    def move_file(self):
        return self.file_controller.move_file_handler()


# expose module-level blueprint for compatibility
file_organization_bp = FileOrganizationRoutes().register()
