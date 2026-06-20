from flask import render_template, redirect, url_for, session


class BaseController:
    """Minimal BaseController to be inherited by concrete controllers.

    Provides small helper wrappers around common Flask response helpers.
    """

    def render(self, template_name, **context):
        return render_template(template_name, **context)

    def redirect(self, endpoint, **kwargs):
        return redirect(url_for(endpoint, **kwargs))

    def get_session_user_id(self):
        return session.get('user_id')

    def get_current_user_id(self):
        return session.get('user_id')
