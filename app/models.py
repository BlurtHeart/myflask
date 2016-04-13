from flask.ext.login import UserMixin, AnonymousUserMixin
from flask import session
from . import login_manager

class Permission:
    FOLLOW = 0X01
    COMMENT = 0X02
    WRITE_ARTICLES = 0X04
    MODERATE_COMMENTS = 0X08
    ADMINSTER = 0X80
    
class Role():
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
class User(UserMixin):
    role = {'permissions':Permission.MODERATE_COMMENTS}
    def __init__(self, id, name, **kwargs):
        print 'id', id, 'name:', name
        self.id = id
        self.name = name
        
        self.role = {'permissions':Permission.FOLLOW}
        for u in user_info:
            if int(id) == u['id']:
                self.role = {'permissions':u['role']}
                break
        super(User, self).__init__(**kwargs)
    def can(self, permissions):
        return self.role is not None and \
               (self.role['permissions'] &permissions) == permissions
    def is_administrator(self):
        return self.can(Permission.ADMINSTER)

@login_manager.user_loader
def load_user(user_id):
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

if __name__ == '__main__':
    print Role.query.filter_by(default=True).first()
    
