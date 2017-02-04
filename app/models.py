from flask.ext.login import UserMixin, AnonymousUserMixin
from flask import session
from . import login_manager, db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Permission:
    FOLLOW = 0X01
    COMMENT = 0X02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINSTER = 0X80
    
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    #users = db.relationship('User', backref='role', lazy='dynamic')
    
    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FOLLOW |
                    Permission.COMMENT |
                    Permission.WRITE_ARTICLES, True),
            'Moderator':(Permission.FOLLOW |
                         Permission.COMMENT |
                         Permission.WRITE_ARTICLES |
                         Permission.MODERATE_COMMENTS, False),
            'Administrator':(0xff, False)
        }
        
user_info = [{'id':1,'name':'abc','passwd':'111111','role':Permission.MODERATE_COMMENTS}]
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
#    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(20), unique=True, index=True)
#    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
#    passwd_hash = db.Column(db.String(128))
#    confirmed = db.Column(db.Boolean, default=False)
#    name = db.Column(db.String(64))
#    location = db.Column(db.String(64))
#    about_me = db.Column(db.Text())
#    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
#    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    
    role = {'permissions':Permission.MODERATE_COMMENTS}
    def __init__(self, id, name, **kwargs):
       # if self.role is None:
       #     self.role = Role.query.filter_by(default=True).first()
        print 'id', id, 'name:', name
        self.id = id
        self.name = name
        
        self.role = {'permissions':Permission.FOLLOW}
        for u in user_info:
            if int(id) == u['id']:
                self.role = {'permissions':u['role']}
                break
        super(User, self).__init__(**kwargs)
    @property
    def password(self):
        raise AttributeError('password is not readable')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.passwd_hash, password)
    
    def can(self, permissions):
        return self.role is not None and \
               (self.role['permissions'] &permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINSTER)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    print 'xxxxxxxxxxxxx load user xxxxxxxxxxxxxxxxxxxx'
    name = ''
    for each in user_info:
        id = int(user_id)
        if id == each['id']:
            name = each['name']
            break
    user = User(user_id, name)
    return user

@login_manager.unauthorized_handler
def unauthorized():
    print 'client unauthorized'
    print 'login session:', session
    return 'unauthorized'
    
