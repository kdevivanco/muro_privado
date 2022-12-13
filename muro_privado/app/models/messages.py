from app.config.connections import MySQLConnection, connectToMySQL
from flask import flash
import re	
from app import app
import pdb
from flask_bcrypt import Bcrypt        
import datetime
from app.models.users import User
import pprint
import time
import math
from datetime import datetime
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 


class Message:

    def __init__(self,data):
        self.id = data['id']
        self.message = data['message']
        self.author_id = data['author_id']
        self.recipient_id = data['recipient_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.deleted_from_reciever = data['deleted_from_reciever']
    
    @classmethod 
    def create_new(cls,form_data,author_id,recipient_id): 
        
        query = '''
                INSERT INTO messages ( message, author_id,recipient_id,deleted_from_reciever,created_at ) 
                VALUES ( %(message)s, %(author_id)s,%(recipient_id)s,'NO', NOW());
                '''

        data = {
                "message": form_data["message"],
                "author_id": author_id,
                "recipient_id": recipient_id,

            }

        results = connectToMySQL('muro_privado').query_db(query,data) #ID 
        
        if results == False:
            flash('Something went wrong','error')
            return False
        
        message = Message.classify_message(results)
        recipient = Message.classify_recipient(results)
        message.recipient = recipient

        flash ('Message sent!','success')

        return message
    
    @classmethod
    def get_sent_time(cls,id): #MESSAGE ID
        query = ''' 
                SELECT created_at FROM messages 
                WHERE id = %(id)s
                '''

        data = {
            'id':id
        }

        results = connectToMySQL('muro_privado').query_db(query,data) #

        return results[0]

    #Construye el objeto Trip con un nuevo viaje, este metodo es llamado por create_new
    @classmethod
    def classify_message(cls,id): #construye trip como objeto de clase Trip
        
        query = '''SELECT * FROM messages 
                JOIN users ON users.id = messages.author_id
                where messages.id = %(id)s '''

        data = {
            "id": id
        }
        results = connectToMySQL('muro_privado').query_db(query,data)
        if results == False:
            print('no message matches id')
            return False
        result = results[0]

        message = cls(result)
        author = User({
            'id': result['users.id'],
            'first_name': result['first_name'],
            'last_name': result['last_name'],
            'email': result['email'],
            'password': result['password'],
            'created_at': result['created_at'],
            'updated_at': result['updated_at']
        })
        
        message.author = author 

        return message

    @classmethod
    def classify_recipient(cls,id): #construye trip como objeto de clase Trip
        
        query = '''SELECT * FROM messages 
                JOIN users ON users.id = messages.recipient_id
                where messages.id = %(id)s '''

        data = {
            "id": id
        }

        results = connectToMySQL('muro_privado').query_db(query,data)
        if len(results) == 0:
            print('no message matches id')
            return False
        result = results[0]

        message = cls(result)
        recipient = User({
            'id': result['users.id'],
            'first_name': result['first_name'],
            'last_name': result['last_name'],
            'email': result['email'],
            'password': result['password'],
            'created_at': result['created_at'],
            'updated_at': result['updated_at']
        })

        return recipient


    @classmethod
    def get_recieved(cls, recipient_id):
        query = '''SELECT messages.id FROM messages 
                JOIN users ON users.id = messages.recipient_id
                where users.id = %(recipient_id)s '''
        
        data = {
            "recipient_id" : recipient_id
        }

        results = connectToMySQL('muro_privado').query_db(query,data)
        recieved_messages = []

        for result in results: 
            message = Message.classify_message(result['id'])
            recipient = Message.classify_recipient(result['id'])
            message.recipient = recipient

            recieved_messages.append(message)
        
        return recieved_messages

    @classmethod
    def sent_count(cls, author_id):
        query = '''SELECT * FROM messages 
                JOIN users ON users.id = messages.author_id
                where users.id = %(author_id)s '''
        
        data = {
            "author_id" : author_id
        }

        results = connectToMySQL('muro_privado').query_db(query,data)

        sent_message_count = 0

        for result in results: 
            sent_message_count +=1
        
        return sent_message_count


    @classmethod
    def get_sent(cls,author_id):
        query = '''SELECT messages.id FROM messages 
                JOIN users ON users.id = messages.author_id
                where users.id = %(author_id)s '''
        
        data = {
            "author_id" : author_id
        }

        results = connectToMySQL('muro_privado').query_db(query,data)
        sent_messages = []
        for result in results:
            message = Message.classify_message(result['id'])
            recipient = Message.classify_recipient(result['id'])
            message.recipient = recipient
            sent_messages.append(message)

        return sent_messages

    @classmethod
    def get_deleted(cls,recipient_id):
        query = '''SELECT messages.id FROM messages 
                JOIN users ON users.id = messages.recipient_id
                where users.id = %(recipient_id)s and messages.deleted_from_reciever = "yes"
                order by messages.created_at desc;
                '''
        
        data = {
            "recipient_id" : recipient_id
        }

        results = connectToMySQL('muro_privado').query_db(query,data)
        deleted_messages = []
        for result in results:
            message = Message.classify_message(result['id'])
            recipient = Message.classify_recipient(result['id'])
            message.recipient = recipient
            deleted_messages.append(message)

        return deleted_messages


    #Borra un mensaje recibido por el usuario
    @classmethod
    def delete(cls,message_id): #message_id
        query = '''UPDATE messages
        SET deleted_from_reciever = 'yes', updated_at = NOW() 
        where id = %(id)s; '''

        data = {
            "id" : message_id
        }
        connectToMySQL('muro_privado').query_db(query,data)
        flash('Deleted message!','success')

        return 
    
    def time_span(self):
        now = datetime.now()
        delta = now - self.created_at
        print(delta.days)
        print(delta.total_seconds())
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif (math.floor(delta.total_seconds() / 60)) >= 60:
            return f"{math.floor(math.floor(delta.total_seconds() / 60)/60)} hours ago"
        elif delta.total_seconds() >= 60:
            return f"{math.floor(delta.total_seconds() / 60)} minutes ago"
        else:
            return f"{math.floor(delta.total_seconds())} seconds ago"