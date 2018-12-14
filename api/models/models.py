# -*- coding: UTF-8 -*-
"""
models.py
- Data classes for the surveyapi application
"""
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash
from flask_security.utils import hash_password, verify_password

app = current_app
db = SQLAlchemy()


def row2dict(row):
    if row is None:
        return ""
    d = {}
    for column in row.__table__.columns:
        if isinstance(getattr(row, column.name), str):
            d[column.name] = getattr(row, column.name)
        elif isinstance(getattr(row, column.name), datetime):
            d[column.name] = str(getattr(row, column.name))
        else:
            # d[column.name] = str(getattr(row, column.name))
            d[column.name] = getattr(row, column.name)
    return d


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_on = db.Column(db.DateTime, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)


class User(Base, db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))
    name = db.Column(db.String(32))
    email = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean, default=True)
    dept = db.column(db.String(32))
    # email = db.Column(db.String(32))
    mobile = db.Column(db.String(32))
    wxid = db.Column(db.String(128))
    xcxid = db.Column(db.String(128))
    UnionID = db.Column(db.String(128))
    wxName = db.Column(db.String(50))
    wxpicurl = db.Column(db.String(128))
    roles = db.relationship(
        'Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.username

    # def verify_pwd(self, pwd):
    #     if self.password == pwd:
    #         return True
    #     return False

    # @property
    # def password_hash(self):
    #     raise AttributeError('password is not a readable attribute')
    #
    # @password_hash.setter
    # def password_hash(self, password):
    #     self.password = generate_password_hash(password)
    #
    # def verify_password(self, password):
    #     return check_password_hash(self.password, password)

    # def generate_auth_token(self, expiration=600):
    #     s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    #     return s.dumps({'id': self.id})  # 返回一个token

    # @staticmethod
    # def verify_auth_token(token):
    #     s = Serializer(app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token)
    #     except SignatureExpired:
    #         return None  # valid token, but expired
    #     except BadSignature:
    #         return None  # invalid token
    #     user = User.query.get(data['id'])
    #     return user


class Role(Base, db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        # return '<role %r>' % self.name
        return self.name

# for flask-security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)



