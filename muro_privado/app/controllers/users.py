from flask import Flask, render_template, request, redirect, Blueprint,session
from app.models.users import User
from app.models.messages import Message
import json

users = Blueprint('users', __name__, template_folder='templates')


@users.route('/')
def landing_page():
    if session['user'] == None:
        log = 'login'
    else:
        log = 'logout'

    return render_template('2register.html', log = log)

@users.route('/register',methods=["POST"])
def register_user():
    if not User.email_free(request.form):
        return redirect('/')
    if not User.validate_user(request.form):
        return redirect('/')
    
    user_id = User.create_new(request.form)
    user = User.get_one(user_id)
    session['user'] = {
            'id': user.id,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email
        }
    
    return redirect('/wall')

@users.route('/login',methods=["POST"])
def login():
    user = User.login(request.form)

    if user != False:
        session['user'] = {
            'id': user.id,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email':user.email
        }
    else:
        return redirect('/')

    return redirect('/wall')


@users.route('/log')
def logout():
    session['user'] = None
    return redirect('/')


