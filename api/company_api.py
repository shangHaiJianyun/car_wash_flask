"""
company_api.py  
- provides the API endpoints for company vehicle user
  REST requests and responses
"""

from flask import Blueprint, jsonify, request, current_app, abort, g
from model.models import *
# from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context
from views import *
from controllers.user_client import *
from controllers.vehicle_fuel import *

company_api = Blueprint('company_api', __name__)


# @company_api.route('/hello/<string:name>/')
# @auth.login_required
# def say_hello(name):
#     # user = User.verify_auth_token(username_or_token)
#     # if not user:
#     #         return False
#     # g.user = user
#     print g.user.username, 'g.user'
#     ug = [x.name for x in g.user.user_group]
#     response = {'status': "success", 'user': g.user.id, 'user_group': ug}
#     return jsonify(response)


@company_api.route('/update_company/<int:id>/', methods=['POST'])
def update_company():
    '''
      update_company  company
      /detail/<int:id>/', methods=['GET']
    '''
    return render_template('hello.html')


@company_api.route('/show_company_qr/<int:id>/', methods=['GET'])
def show_company_qr(id):
    '''
        upload vehicle csv file
    '''
    return


@company_api.route('/upload_vehicle/', methods=['POST'])
def upload_vehicle():
    '''
        upload vehicle csv file
    '''
    return


@company_api.route('/update_vehicle/<int:id>/', methods=['POST'])
def update_vehicle():
    '''
        update vehicle record
    '''
    return


@company_api.route('/fuel_overview/', methods=['GET'])
def fuel_overview():
    '''
        fuel report for all
    '''
    return


@company_api.route('/fuel_record_overview/', methods=['GET'])
def fuel_record_overview():
    '''
        fuel report for all vehicles
    '''
    return


@company_api.route('/show_fuel_record/<int:id>/', methods=['GET'])
def show_fuel_record():
    '''
        show vehicle fuel_record
    '''
    return


@company_api.route('/vehicle_fuel_history/<int:id>/', methods=['GET'])
def vehicle_fuel_history(id):
    '''
        show vehicle fuel rate
    '''
    pass


@company_api.route('/vehicle_fuel_rate/<int:id>/', methods=['GET'])
def vehicle_fuel_rate(id):
    vehicle = VehicleM()
    res = vehicle.user_vehicles(id)
    return jsonify({"data": res})
