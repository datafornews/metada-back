# Define models
# https://github.com/flask-admin/flask-admin/blob/master/examples/auth/app.py
import os
import jwt
import datetime

from app import app, db, bcrypt
from flask_security import UserMixin, RoleMixin
from flask_security.utils import hash_password

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Role {} {} at {} >'.format(
            self.id, self.name, id(self))


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    registered_on = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    entities_created = db.relationship('Entity', backref='created_by',
                                       lazy='dynamic', primaryjoin='User.id==Entity.created_by_id')
    entities_updated = db.relationship('Entity', backref='updated_by',
                                       lazy='dynamic', primaryjoin='User.id==Entity.updated_by_id')
    edges_created = db.relationship('Edge', backref='created_by',
                                    lazy='dynamic', primaryjoin='User.id==Edge.created_by_id')
    edges_updated = db.relationship('Edge', backref='updated_by',
                                    lazy='dynamic', primaryjoin='User.id==Edge.updated_by_id')
    verified_email = db.relationship(
        "VerifiedEmail", uselist=False, backref="user")

    def set_password(self, password):
        self.password = hash_password(password)

    def __init__(self,
                 email=None,
                 password=None,
                 first_name=None,
                 last_name=None,
                 active=None,
                 confirmed_at=None,
                 registered_on=None,
                 roles=['user']
                 ):
        self.email = email
        self.password = hash_password(password)
        self.registered_on = datetime.datetime.now()
        self.first_name = first_name
        self.last_name = last_name
        self.active = active
        self.roles = [r for r in Role.query.all() if r.name in roles]

    def __str__(self):
        return self.email

    def __repr__(self):
        return '<User {} at {}>'.format(
            self.email, id(self)
        )

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False


class VerifiedEmail(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    link = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime())

    def __init__(self, link=None, user_id=None, created_at=None):
        self.created_at = created_at
        self.link = link
        self.user_id = user_id

    def __repr__(self):
        return '<' + self.link[:5] + '... for ' + self.user.email + '>'
