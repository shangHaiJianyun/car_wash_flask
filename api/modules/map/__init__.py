from flask import Blueprint

map_blu = Blueprint('map', __name__)

from .views import *
