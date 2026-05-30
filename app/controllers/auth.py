from flask import render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.controllers.base_controller import BaseController
from app.models.database import (
    get_user_by_identifier,
    get_user_by_email,
    get_user_by_username,
    create_user,
)
import re


class AuthController(BaseController):
    def login(self):
        if session.get('user_id'):
            return redirect(url_for('home.profile'))

        if request.method == 'POST':
            identifier = (request.form.get('identifier') or '').strip()
            password = request.form.get('password', '')

            if not identifier or not password:
                return render_template('login.html', active_form='sign-in', login_error='Please enter your email or username and password.'), 400

            user = get_user_by_identifier(identifier)
            if not user or not check_password_hash(user['password_hash'], password):
                return render_template('login.html', active_form='sign-in', login_error='Invalid credentials. Please try again.'), 401

            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            return redirect(url_for('home.profile'))

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
        return redirect(url_for('home.profile'))

    def reset_password(self):
        return render_template('reset.html')

    def logout(self):
        session.clear()
        return redirect(url_for('auth.login'))
