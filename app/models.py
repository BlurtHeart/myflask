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
    users = db.relationship('User', backref='role', lazy='dynamic')
    
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
        for r in roles:
            role = Role.query.filter_by(role_name=r).first()
            if role is None:
                role = Role(role_name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

        
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
#    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(20), index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    passwd_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
#    name = db.Column(db.String(64))
#    location = db.Column(db.String(64))
#    about_me = db.Column(db.Text())
#    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    
    # role = {'permissions':Permission.MODERATE_COMMENTS}
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
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

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

    def generate_auth_token(self, expires_in=300):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id':self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

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
        db.session.commit()
        return True
    
    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions &permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINSTER)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_follwed(self, user):
        return self.followers.filter_by(follwer_id=user.id).first() is not None

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    abort(403)
    
