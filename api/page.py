# -*- coding: utf-8 -*-
"""
page.py  
- provides the API endpoints for operations
  REST requests and responses
"""

from flask import Blueprint, jsonify, request
from flask import render_template
from model.models import db, row2dict
from flask_security import auth_token_required
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, roles_required, current_user
# from model.models import *

page = Blueprint('page_bp', __name__, template_folder='templates')


@page.route('/home/')
@login_required
def home():
        # return 'home'
    user = current_user
    userinfo = row2dict(user)
    res = {'user': userinfo}
    return jsonify(res)
    # return render_template('hello.html')


@page.route('/list_company/')
def list_company():
    '''
      list all company
    '''
    # return 'home'
    return render_template('hello.html')


@page.route('/add_company/')
def add_company():
    '''
      add  company
    '''
    return render_template('hello.html')


@page.route('/update_company/<int:id>/', methods=['POST'])
def update_company():
    '''
      update_company  company
      /detail/<int:id>/', methods=['GET']
    '''
    return render_template('hello.html')


@page.route('/del_company/<int:id>/', methods=['POST'])
def del_company():
    '''
      update_company  company
    '''
    return render_template('hello.html')
