from . import db,login_manager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class Role(db.Model):
    __tablename__ = 'roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)

    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>'%self.name

class User(UserMixin,db.Model):
    __tablename__='users'
    id=db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username=db.Column(db.String(64),unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    role_id=db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>'%self.username

    @property
    def password(self):
        raise ArithmeticError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash,password)

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        token = s.dumps({'confirm':self.id})
        return token



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))