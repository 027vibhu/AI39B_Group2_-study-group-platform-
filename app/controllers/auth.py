from flask import render_template, request, session, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.controllers.base_controller import BaseController
from app.models.database import (
    get_user_by_identifier,
    get_user_by_email,
    get_user_by_username,
    create_user,
    update_user_password_by_email,
)
from app.models.deactivated_account import is_deactivated
from app.utils.email import send_reset_code
import re
import time
import secrets

# How long a reset code stays valid (seconds)
RESET_CODE_TTL = 600


class AuthController(BaseController):
    def login(self):
        if session.get('user_id'):
            return redirect(url_for('home.dashboard'))

        if request.method == 'POST':
            identifier = (request.form.get('identifier') or '').strip()
            password = request.form.get('password', '')

            if not identifier or not password:
                return render_template('login.html', active_form='sign-in', login_error='Please enter your email or username and password.'), 400

            user = get_user_by_identifier(identifier)
            if not user or not check_password_hash(user['password_hash'], password):
                return render_template('login.html', active_form='sign-in', login_error='Invalid credentials. Please try again.'), 401

            if is_deactivated(user['id']):
                return render_template('login.html', active_form='sign-in', login_error='This account has been deactivated and cannot be accessed.'), 403

            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user.get('role', 'user')
            return redirect(url_for('home.dashboard'))

        return render_template('login.html', active_form='sign-in')

    def register(self):
        # registration handled via POST on the same login page
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password', '')

        if not username or not email or not password:
            return render_template('login.html', active_form='sign-up', register_error='All fields are required to create an account.'), 400

        if len(username) < 3:
            return render_template('login.html', active_form='sign-up', register_error='Username must be at least 3 characters long.'), 400

        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            return render_template('login.html', active_form='sign-up', register_error='Enter a valid email address.'), 400

        if len(password) < 6:
            return render_template('login.html', active_form='sign-up', register_error='Password must be at least 6 characters long.'), 400

        if get_user_by_username(username):
            return render_template('login.html', active_form='sign-up', register_error='That username is already in use.'), 409

        if get_user_by_email(email):
            return render_template('login.html', active_form='sign-up', register_error='That email is already registered.'), 409

        user_id = create_user(username, email, generate_password_hash(password))
        session['user_id'] = user_id
        session['username'] = username
        session['email'] = email
        session['role'] = 'user'
        return redirect(url_for('home.profile'))

    def reset_password(self):
        return render_template('reset.html')

    def send_reset_code(self):
        """Step 1: generate a code, email it via Resend, store it in the session."""
        email = (request.form.get('email') or '').strip().lower()

        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            return jsonify(ok=False, error='Enter a valid email address.'), 400

        user = get_user_by_email(email)
        if not user:
            return jsonify(ok=False, error='No account is registered with that email.'), 404

        code = f"{secrets.randbelow(1000000):06d}"
        session['reset_email'] = email
        session['reset_code'] = code
        session['reset_expires'] = time.time() + RESET_CODE_TTL
        session['reset_verified'] = False

        ok, err = send_reset_code(email, code)
        if not ok:
            return jsonify(ok=False, error=err or 'Could not send the email.'), 502

        return jsonify(ok=True), 200

    def verify_reset_code(self):
        """Step 2: check the 6-digit code against the one stored in the session."""
        code = (request.form.get('code') or '').strip()
        stored = session.get('reset_code')
        expires = session.get('reset_expires', 0)

        if not stored or time.time() > expires:
            return jsonify(ok=False, error='Your code has expired. Please request a new one.'), 400

        if not code or code != stored:
            return jsonify(ok=False, error='Incorrect code. Please try again.'), 400

        session['reset_verified'] = True
        return jsonify(ok=True), 200

    def set_new_password(self):
        """Step 3: update the password once the code has been verified."""
        if not session.get('reset_verified'):
            return jsonify(ok=False, error='Please verify your code first.'), 403

        email = session.get('reset_email')
        expires = session.get('reset_expires', 0)
        if not email or time.time() > expires:
            return jsonify(ok=False, error='Your reset session has expired. Please start over.'), 400

        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if len(password) < 6:
            return jsonify(ok=False, error='Password must be at least 6 characters long.'), 400
        if password != confirm:
            return jsonify(ok=False, error='Passwords do not match.'), 400

        update_user_password_by_email(email, generate_password_hash(password))

        # Clear all reset state so the code can't be reused.
        for key in ('reset_email', 'reset_code', 'reset_expires', 'reset_verified'):
            session.pop(key, None)

        return jsonify(ok=True), 200

    def logout(self):
        session.clear()
        return redirect(url_for('auth.login'))
