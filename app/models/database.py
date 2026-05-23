from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    school = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    profile_picture_url = db.Column(db.String(500), nullable=True)