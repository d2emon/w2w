from flask import render_template
from flask_mail import Message
from web import mail
from config import ADMINS
from web.decorators import async


@async
def send_async_mail(msg):
    return mail.send(msg)


def send_mail(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_mail(msg)


def follower_notification(followed, follower):
    send_mail(
        "[microblog] {} is now following you!".format(follower.nickname),
        ADMINS[0],
        [followed.email],
        render_template(
            "follower_email.txt",
            user=followed,
            follower=follower,
        ),
        render_template(
            "follower_email.html",
            user=followed,
            follower=follower,
        ),
    )
