from functools import wraps
from flask import abort
from flask.ext.login import current_user
from models import Permission

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print 'xxxxxxxxxxxxx', current_user
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    print 'xxxxxxxxxxxxxxxxxxx', current_user
    return permission_required(Permission.ADMINSTER)(f)