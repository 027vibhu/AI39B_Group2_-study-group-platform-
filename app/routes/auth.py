import re

from flask import Blueprint, render_template, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.database import (
    create_user,
    get_user_by_email,
    get_user_by_identifier,
    get_user_by_username,
)

bp = Blueprint('auth', __name__)


@bp.route('/login')
def login():
    return render_template('login.html', active_form='sign-in')


@bp.route('/login', methods=['POST'])
def login_post():
    identifier = request.form.get('identifier', '').strip()
    password = request.form.get('password', '')

    if not identifier or not password:
        return render_template(
            'login.html',
            active_form='sign-in',
            login_error='Please enter your email or username and password.',
        ), 400

    user = get_user_by_identifier(identifier)
    if not user or not check_password_hash(user['password_hash'], password):
        return render_template(
            'login.html',
            active_form='sign-in',
            login_error='Invalid credentials. Please try again.',
        ), 401

    session['user_id'] = user['id']
    session['username'] = user['username']
    session['email'] = user['email']
    return redirect(url_for('home.profile'))


@bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not username or not email or not password:
        return render_template(
            'login.html',
            active_form='sign-up',
            register_error='All fields are required to create an account.',
        ), 400

    if len(username) < 3:
        return render_template(
            'login.html',
            active_form='sign-up',
            register_error='Username must be at least 3 characters long.',
        ), 400

    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return render_template(
            'login.html',
            active_form='sign-up',
            register_error='Enter a valid email address.',
        ), 400

    if len(password) < 6:
        return render_template(
            'login.html',
            active_form='sign-up',
            register_error='Password must be at least 6 characters long.',
        ), 400

    if get_user_by_username(username):
        return render_template(
            'login.html',
            active_form='sign-up',
            register_error='That username is already in use.',
        ), 409

    if get_user_by_email(email):
        return render_template(
            'login.html',
            active_form='sign-up',
            register_error='That email is already registered.',
        ), 409

    user_id = create_user(username, email, generate_password_hash(password))
    session['user_id'] = user_id
    session['username'] = username
    session['email'] = email
    return redirect(url_for('home.profile'))


@bp.route('/reset_password')
def reset_password():
    return render_template('reset.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
