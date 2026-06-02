from flask import render_template, redirect, url_for, session, request, flash


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

    def get_form_data(self, *fields):
        return tuple(request.form.get(f, '').strip() for f in fields)

    def is_logged_in(self):
        return 'user_id' in session

    def get_current_user_id(self):
        return session.get('user_id')

    def flash_and_redirect(self, msg, category, endpoint):
        flash(msg, category)
        return redirect(url_for(endpoint))
