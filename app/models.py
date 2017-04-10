from flask_login import UserMixin, AnonymousUserMixin
from flask import session, abort, current_app
from . import login_manager, db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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
        
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
#    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(20), index=True)
#    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    passwd_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
#    name = db.Column(db.String(64))
#    location = db.Column(db.String(64))
#    about_me = db.Column(db.Text())
#    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
#    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    
    role = {'permissions':Permission.MODERATE_COMMENTS}
    def __init__(self, **kwargs):
       # if self.role is None:
       #     self.role = Role.query.filter_by(default=True).first()
        # print 'id', id, 'name:', name
        # self.id = id
        # self.name = name
        
        # self.role = {'permissions':Permission.FOLLOW}
        # for u in user_info:
        #     if int(id) == u['id']:
        #         self.role = {'permissions':u['role']}
        #         break
        # super(User, self).__init__(**kwargs)
        super(User, self).__init__(**kwargs)
    @property
    def password(self):
        raise AttributeError('password is not readable')
    @password.setter
    def password(self, password):
        self.passwd_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.passwd_hash, password)

    def generate_confirmation_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
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
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    abort(403)
    
