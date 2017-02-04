from flask import Blueprint

base = Blueprint('base', __name__)

from . import base_views

from ..models import Permission
@base.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)