from flask import Blueprint

api = Blueprint('api_v1.0', __name__)

from . import views
