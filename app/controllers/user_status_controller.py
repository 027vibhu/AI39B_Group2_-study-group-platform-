from app.controllers.base_controller import BaseController
from app.models.user_status_model import UserStatusModel
from flask import jsonify, render_template

class UserStatusController(BaseController):
    def _init_(self):
        super()._init_()
        # Instantiate your database model
        self.model = UserStatusModel()

    def get_online_status_page(self):
        """
        Fetches all online members using raw SQL through the model
        and renders the HTML template for Urbi's frontend.
        """
        online_members = self.model.get_online_members()
        return render_template("online_members.html", members=online_members)

    def update_status_api(self, user_id, is_online):
        """
        An API endpoint that Almira's backend or JavaScript actions can hit
        to change a user's status dynamically.
        """
        self.model.update_user_status(user_id, is_online)
        return jsonify({"status": "success", "message": "User status updated securely"})