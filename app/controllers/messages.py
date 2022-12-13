from flask import Flask, render_template, request, redirect, Blueprint,session
from app.models.users import User
from app.models.messages import Message
import json
import pdb

messages = Blueprint('messages', __name__, template_folder='templates')


@messages.route('/wall')
def welcome_user():

    if session['user'] == None:
        return redirect('/')
    log = 'logout'
    user = session['user']

    friends = User.get_all()

    recieved_messages = Message.get_recieved(user['id'])
    recieved_count = len(recieved_messages)
    sent_count = Message.sent_count(user['id'])
    for message in recieved_messages:
        print(message.id)
    return render_template('3wall.html',log= log, friends = friends, user = user, recieved_messages = recieved_messages, recieved_count = recieved_count, sent_count = sent_count)



@messages.route('/sendmsg/<recipient_id>', methods=['POST'])
def send_message(recipient_id):
    author_id = session['user']['id']
    message_id = Message.create_new(request.form,author_id,recipient_id)

    return redirect('/wall')


@messages.route('/delete/<id>')
def delete_recieved_message(id):
    if session['user'] == None:
        log = 'login'
        return redirect('/')

    Message.delete(id)

    return redirect('/wall')


@messages.route('/sent/<author_id>')
def show_sent_msgs(author_id):
    if session['user'] == None:
        log = 'login'
        return redirect('/')

    user = session['user']
    sent_messages = Message.get_sent(author_id)

    return render_template('4sent.html', user=user,sent_messages=sent_messages)    

@messages.route('/history/<recipient_id>')
def deleted_messages(recipient_id):
    if session['user'] == None:
        log = 'login'
        return redirect('/')

    user = session['user']
    deleted_messages = Message.get_deleted(recipient_id)

    return render_template('5deleted.html', user=user,deleted_messages=deleted_messages)   

