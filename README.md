# Flask Architecture Blueprint — Copyable Guide

This README is a practical, copy-friendly blueprint you can follow to recreate this app's architecture in a new repository. It emphasizes simple, repeatable patterns so you can scaffold by hand or script.

---

## Overview

- App factory with blueprints
- Controllers as classes (inherit from `BaseController` for shared helpers)
- Models using a small PyMySQL `Database` wrapper and an abstract `BaseModel` (no ORM)
- Routes are thin blueprint wrapper classes

## Prerequisites

- Python 3.10+
- MySQL server (or compatible) running and accessible
- Recommended packages in `requirements.txt`:

```text
Flask==3.1.0
pymysql
werkzeug
```

Install into a virtualenv:

```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Recommended project layout

```
run.py
config.py
requirements.txt
app/
  __init__.py
  auth.py                # session decorators (login_required, admin_required)
  controllers/
    base_controller.py
    auth.py
    # add feature controllers here (e.g. items.py, orders.py)
  models/
    base_model.py
    database.py
    # add feature models here (e.g. item.py, order.py)
  routes/
    auth.py
    # add feature route wrappers here (e.g. items.py, orders.py)
  templates/
    base.html
    login.html
    register.html
    dashboard.html
    profile.html
    # add feature templates under feature-specific subfolders
  static/
    css/style.css
```

Keep filenames and structure consistent so you can copy controllers/routes without change.

---

## Copy-ready code snippets (minimal, pasteable)

1) `run.py`

```python
from app import create_app
app = create_app()

if __name__ == '__main__':
  app.run(debug=True)
```

2) `config.py` (local settings — edit values)

```python
SECRET_KEY = 'change-me'
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'change-me'
MYSQL_DATABASE = 'APP_DB'
```

3) `app/__init__.py` (app factory)

```python
from flask import Flask
from app.models.database import Database
from app.routes.auth import AuthRoutes
from app.routes.product import ProductRoutes

import config

def create_app():
  app = Flask(__name__)
  app.secret_key = config.SECRET_KEY
  with app.app_context():
    Database.create_tables()

  app.register_blueprint(AuthRoutes().register())
  return app
```

4) `app/models/database.py` (single-file DB wrapper)

```python
import pymysql
import config

class Database:
  def __init__(self):
    self.__connection = pymysql.connect(
      host=config.MYSQL_HOST,
      user=config.MYSQL_USER,
      password=config.MYSQL_PASSWORD,
      database=config.MYSQL_DATABASE,
      cursorclass=pymysql.cursors.DictCursor,
    )

  def fetch_one(self, query, params=None):
    cur = self.__connection.cursor()
    cur.execute(query, params)
    r = cur.fetchone()
    cur.close()
    return r

  def fetch_all(self, query, params=None):
    cur = self.__connection.cursor()
    cur.execute(query, params)
    r = cur.fetchall()
    cur.close()
    return r

  def execute(self, query, params=None):
    cur = self.__connection.cursor()
    cur.execute(query, params)
    self.__connection.commit()
    cur.close()

  def close(self):
    self.__connection.close()

  @staticmethod
  def create_tables():
    db = Database()
    db.execute('''
      CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''')
    db.close()
```

5) `app/models/base_model.py` (abstract helpers)

```python
from abc import ABC, abstractmethod
from app.models.database import Database

class BaseModel(ABC):
  @property
  @abstractmethod
  def table(self):
    pass

  def find_by_id(self, id_):
    db = Database()
    r = db.fetch_one(f"SELECT * FROM {self.table} WHERE id = %s", (id_,))
    db.close()
    return r

  def find_by(self, column, value):
    db = Database()
    r = db.fetch_one(f"SELECT * FROM {self.table} WHERE {column} = %s", (value,))
    db.close()
    return r

  def find_all(self, order_by='id'):
    db = Database()
    r = db.fetch_all(f"SELECT * FROM {self.table} ORDER BY {order_by}")
    db.close()
    return r

  def count_all(self):
    db = Database()
    r = db.fetch_one(f"SELECT COUNT(*) AS total FROM {self.table}")
    db.close()
    return r['total']
```

6) `app/models/user.py` (concrete example)

```python
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.base_model import BaseModel
from app.models.database import Database

class User(BaseModel):
  @property
  def table(self):
    return 'users'

  def __init__(self, name=None, email=None, password=None, role='user'):
    self.name = name
    self.email = email
    self.__password = None
    self.role = role
    if password:
      self.set_password(password)

  def set_password(self, plain):
    self.__password = generate_password_hash(plain)

  def check_password(self, plain):
    if self.__password is None:
      return False
    return check_password_hash(self.__password, plain)

  def save(self):
    db = Database()
    db.execute('INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)',
           (self.name, self.email, self.__password, self.role))
    db.close()

  @classmethod
  def from_db(cls, data):
    if not data:
      return None
    u = cls()
    u.name = data['name']
    u.email = data['email']
    u.__password = data['password']
    u.role = data['role']
    return u
```

7) `app/controllers/base_controller.py`

```python
from flask import request, session, flash, redirect, url_for

class BaseController:
  def get_form_data(self, *fields):
    return tuple(request.form.get(f, '').strip() for f in fields)

  def is_logged_in(self):
    return 'user_id' in session

  def get_current_user_id(self):
    return session.get('user_id')

  def flash_and_redirect(self, msg, category, endpoint):
    flash(msg, category)
    return redirect(url_for(endpoint))
```

8) `app/controllers/auth.py` (minimal controller)

```python
from flask import render_template, request, session, redirect, url_for, flash
from app.controllers.base_controller import BaseController
from app.models.user import User

class AuthController(BaseController):
  def __init__(self):
    self.user_model = User()

  def login(self):
    if request.method == 'POST':
      email, password = self.get_form_data('email','password')
      row = self.user_model.find_by('email', email)
      if row:
        u = User.from_db(row)
        if u.check_password(password):
          session['user_id'] = row['id']
          session['user_name'] = row['name']
          session['role'] = row['role']
          return self.flash_and_redirect('Logged in', 'success', 'auth.dashboard')
      flash('Invalid', 'danger')
    return render_template('login.html')

  def register(self):
    if request.method == 'POST':
      name, email = self.get_form_data('name','email')
      password = request.form.get('password','')
      u = User(name=name, email=email, password=password)
      if u.email_exists():
        flash('Email exists', 'danger')
        return redirect(url_for('auth.register'))
      u.save()
      return self.flash_and_redirect('Registered', 'success', 'auth.login')
    return render_template('register.html')

  def logout(self):
    session.clear()
    return self.flash_and_redirect('Logged out', 'success', 'auth.login')

  def dashboard(self):
    total = self.user_model.count_all()
    return render_template('dashboard.html', total_users=total)
```

9) `app/routes/auth.py` (routes → controller mapping)

```python
from flask import Blueprint
from app.controllers.auth import AuthController
from app.auth import login_required

class AuthRoutes:
  def __init__(self):
    self.bp = Blueprint('auth', __name__)
    self.controller = AuthController()

  def register(self):
    self.bp.route('/login', methods=['GET','POST'])(self.controller.login)
    self.bp.route('/register', methods=['GET','POST'])(self.controller.register)
    self.bp.route('/dashboard')(login_required(self.controller.dashboard))
    self.bp.route('/logout')(self.controller.logout)
    return self.bp
```

10) `app/auth.py` (session decorators)

```python
from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    if 'user_id' not in session:
      flash('Please login', 'warning')
      return redirect(url_for('auth.login'))
    return f(*args, **kwargs)
  return wrapper

def admin_required(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    if 'user_id' not in session or session.get('role') != 'admin':
      flash('Admin required', 'danger')
      return redirect(url_for('auth.login'))
    return f(*args, **kwargs)
  return wrapper
```

---

## Feature blueprint (step-by-step)

1. Add the model in `app/models/` (inherit `BaseModel` if you need the helpers).
2. Add a controller class in `app/controllers/` (inherit `BaseController` for session/form helpers).
3. Add templates under `app/templates/<feature>/` and extend `base.html`.
4. Add a route wrapper in `app/routes/` that maps URLs to controller methods and returns a Blueprint.
5. Register the blueprint in `app/__init__.py`.

---


