import json,os,django
import pika
from decouple import config

# import django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE","project_core.settings")
django.setup()

from escrow_app import models

params = pika.URLParameters(config('AMPQ_URL'))
connection  = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='app')

def callback(ch, method, properties, body):

    data = json.loads(body)
    
    # create a user from User App
    if properties.content_type == 'user_created':
        models.AppUsers.objects.create(
            app_user=data['id'],
            email=data['email'],
            reference_id=data['reference_id']
        )
        print("saved user")
        
    # update user is_verified properties to  True
    elif properties.content_type == 'verify_account':
        user = models.AppUsers.objects.get(app_user=data)
        user.is_verified = True
        user.save()
        print("verify user")
    
    # save user profile from User App
    elif properties.content_type == 'save_user_profile':
        print("I saved user profile")
        
    # update user profile from User App
    elif properties.content_type == 'update_user_profile':
        print("i updated user profile")
        
    
channel.basic_consume(queue='app', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
channel.close()