"""Module providing an email framework for the app."""
from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """Send an email, using the pre-set email configuration.

    Using the email configuration in config.py,  the relevent environmental
    variables, and Flask-Mail, a message is built using the provided arguments
    and sent.
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[sbMACRO] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('templates/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('templates/reset_password.html',
                                         user=user, token=token))