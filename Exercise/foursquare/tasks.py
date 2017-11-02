from __future__ import absolute_import, unicode_literals
from django.utils import timezone
from django.contrib.auth.models import User
from dateutil import relativedelta
from django.core.mail import send_mail
from celery import shared_task
import datetime


@shared_task()
def send_mail_to_non_visitor_users():
    now = datetime.date.today()
    three_months_ago = now - datetime.timedelta(days=3*365/12)
    users = User.objects.filter(last_login__lte=three_months_ago)
    user_mail_list = get_mail_list_from_users(users)
    send_mail('hi', 'why don\'t u visit my site? its so good', 'from@example.com', user_mail_list)


@shared_task()
def send_mail_to_user_before_birthday():

    tomorrow = datetime.date.today()+datetime.timedelta(days=1)
    users = User.objects.filter(profile__date_of_birth__day__lte=tomorrow.day,
                                profile__date_of_birth__month=tomorrow.month)
    print(users)
    user_mail_list = get_mail_list_from_users(users)
    send_mail('hi', 'happy birthday!', 'from@example.com', user_mail_list)


def get_mail_list_from_users(users):
    user_mail_list = []
    for user in users:
        user_mail_list.append(user.email)
        print("mail will be sent to this guy: " + str(user.username) + "," + str(user.email))
    return user_mail_list

