from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Permission:
    ADMIN = 1    # 001: 管理員
    BOOK = 2     # 010: 預約權限
    VIEW = 4     # 100: 查看權限

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False) 
    permission_mask = db.Column(db.Integer, default=4)

class Space(db.Model):
    __tablename__ = 'spaces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    is_hidden = db.Column(db.Boolean, default=False)
    resources = db.relationship('Resource', backref='space', cascade="all, delete-orphan")

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    is_hidden = db.Column(db.Boolean, default=False)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    attendees = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='bookings')
    resource = db.relationship('Resource', backref=db.backref('bookings', cascade="all, delete-orphan"))