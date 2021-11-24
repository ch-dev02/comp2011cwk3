from werkzeug.utils import unescape
from app import db
from flask_login import UserMixin

# This is used to model the database with a table called Task
# with the columns outlined by the coursework specification
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    deadline = db.Column(db.DateTime)
    description = db.Column(db.String(500))
    complete = db.Column(db.Boolean)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    code = db.Column(db.String(500), unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(500), unique=True)
    password = db.Column(db.String(500))

class UserGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user = db.relationship('User')
    group = db.relationship('Group')