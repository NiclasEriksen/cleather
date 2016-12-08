from flask import render_template
from config import ADMINS
from flask_mail import Message
from app import app, mail
from .decorators import async


@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)


def follower_notification(followed, follower):
    send_email(
        "[Cleather] {0} is now following you!".format(
            follower.nickname
        ),
        [followed.email],
        render_template(
            "follower_email.txt",
            user=followed, follower=follower
        ),
        render_template(
            "follower_email.html",
            user=followed, follower=follower
        )
    )
