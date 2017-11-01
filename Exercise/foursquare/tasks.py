from __future__ import absolute_import, unicode_literals
from .models import Profile
from django.utils import timezone
from django.contrib.auth.models import User
from dateutil import relativedelta
from django.core.mail import send_mail
from celery import shared_task


@shared_task()
def mail_to_non_visitor_users():
    now = timezone.now()
    users = User.objects.all()
    user_last_login_dates = []
    user_mail_addresses = []
    for user in users:
        user_last_login_dates.append(user.last_login)
    for date in user_last_login_dates:
        time_passed_in_months = relativedelta.relativedelta(now, date).months
        if int(time_passed_in_months) >= 3:
            user_mail = User.objects.filter(last_login=date).email
            user_mail_addresses.append(user_mail)
            print("email sent to " + str(user_mail))
        else:
            print("not more than 2 months, nice")
    send_mail('hi', 'why don\'t u visit my site? its so good', 'from@example.com', user_mail_addresses)


@shared_task()
def mail_to_user_before_birthday():
    now = timezone.now()
    users = User.objects.all()
    user_mail_addresses = []
    date_of_birthdays = []
    for user in users:
        date_of_birthdays.append(user.profile.date_of_birth)
    date_of_birthdays = list(set(date_of_birthdays))
    print("date of birthdays:")
    print(date_of_birthdays)
    for date in date_of_birthdays:
        if now.day-date.day >= 1:
            birthday_profiles = Profile.objects.filter(date_of_birth=date)
            for profile in birthday_profiles:
                user_mail_addresses.append(profile.user.email)
                print("email sent to birthday guy! :" + str(profile.user.email))
        else:
            print("its no ones birthday")
    user_mail_addresses = list(set(user_mail_addresses))  # remove duplicates
    send_mail('hi', 'happy birthday!', 'from@example.com', user_mail_addresses)
    print("email sent to these guys: ")
    print(user_mail_addresses)
