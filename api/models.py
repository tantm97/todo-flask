import re

from passlib.apps import custom_app_context as password_context

from api.extension import db


class ResourceAddUpdateDelete():
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()


class User(db.Model, ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # I save the hash for the password (I don't persist the actual password)
    password_hash = db.Column(db.String(120), nullable=False)
    creation_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    max_todo = db.Column(db.Integer, nullable=False)

    def verify_password(self, password):
        return password_context.verify(password, self.password_hash)

    def check_password_strength_and_hash_if_ok(self, password):
        if len(password) < 8:
            return 'The password is too short. Please, specify a password with at least 8 characters.', False
        if len(password) > 32:
            return 'The password is too long. Please, specify a password with no more than 32 characters.', False
        if re.search(r'[A-Z]', password) is None:
            return 'The password must include at least one uppercase letter.', False
        if re.search(r'[a-z]', password) is None:
            return 'The password must include at least one lowercase letter.', False
        if re.search(r'\d', password) is None:
            return 'The password must include at least one number.', False
        if re.search(r"[ @!#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None:
            return 'The password must include at least one symbol.', False
        self.password_hash = password_context.hash(password)
        return '', True

    def __init__(self, name, max_todo):
        self.name = name
        self.max_todo = max_todo
    

class Task(db.Model, ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(250), nullable=False)
    creation_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy='dynamic' , order_by='Task.message'))

    def __init__(self, message, user):
        self.message = message
        self.user = user
