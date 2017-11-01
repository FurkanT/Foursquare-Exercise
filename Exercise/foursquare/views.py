from django.shortcuts import render, redirect
from .models import LocationSearch,Profile
from .forms import LocationForm
import requests
from operator import itemgetter
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.http import HttpResponse
from .forms import SignUpForm, ImageUploadForm, ChangeEmailForm
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django import forms
from dateutil import relativedelta
from django.core.mail import send_mail


def login(request):
    username = request.POST['username']
    password = request.POST['password']
    print(username + password)
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
                auth_login(request, user)
        else:
            return HttpResponse('<h1>disabled account</h1>')
    else:
        return HttpResponse('<h1>Invalid login</h1>')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.date_of_birth = form.cleaned_data.get('date_of_birth')
            print(user.profile.date_of_birth)
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
    context = {
                'form': form,
    }
    return render(request, 'foursquare/signup.html', context)


def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user_id = request.user.id
            user = User.objects.get(pk=user_id)
            user.profile.avatar = form.cleaned_data['avatar']
            user.save()
            print('valid image save?')
            return redirect('/')
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {'form': form})


def search(request):
    mail_to_user_before_birthday()
    mail_to_non_visitor_users()
    print("User: " + str(request.user))
    current_user = request.user
    if not current_user.is_anonymous():
        user_searches = get_user_searches(current_user)
        # if it_is_birthday(current_user):
        #     context = {
        #         'age': get_age(current_user),
        #         'user_name': current_user.username,
        #     }
        #     return render(request, 'foursquare/birthdaypage.html', context)
        print("User searches in view: "+str(user_searches))
    else:
        user_searches = ""
    recent_searches = get_recent_searches()
    form = LocationForm(request.GET)
    if not form.is_valid():
        form = LocationForm()
        context = {
            'recent_searches': recent_searches,
            'form_box': form,
            'user_searches': user_searches,
        }
        return render(request, 'foursquare/maintemp.html', context)
    print("form is valid")
    cd = form.cleaned_data
    food = cd['food']
    location = cd['location']
    print(food, location)
    offset = request.GET.get('offset')
    if offset is None:
        offset = 0
    data = get_response(food, location, offset)
    total_results = get_total_results(data)
    print(total_results)
    venue_list = get_venue_list(data)
    sorted_list = get_sorted_list(venue_list)
    if total_results != 0:
        current_search = get_and_save_the_obj(food, location, current_user)
    else:
        current_search = None
    print(offset)
    if int(offset) < 10:
        prev_offset = None
    else:
        prev_offset = int(offset) - 10
        if prev_offset == 0:        # this means if offset = 10, so in second page i want to show "previous"
            prev_offset = str(0)    # but if i don't make it a string prev_offset will be recognized as None
    if int(offset) >= total_results - 10:
        next_offset = None
    else:
        next_offset = int(offset) + 10
    context = {
        'venue_list': sorted_list,
        'recent_searches': recent_searches,
        'form_box': form,
        'next_offset': next_offset,
        'prev_offset': prev_offset,
        'current_search': current_search,
        'total_venue_count': total_results,
        'user_searches': user_searches,
    }
    return render(request, 'foursquare/maintemp.html', context)


def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data.get("new_email")
            if not User.objects.filter(email=new_email):
                request.user.email = new_email
                request.user.save()
                print("password is now: "+str(request.user.email))
                return redirect('/')
            raise forms.ValidationError('This email address is already in use.')
    else:
        form = ChangeEmailForm()
        return render(request, 'foursquare/emailchangepage.html', {'form': form})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            #messages.success(request, 'Your password was successfully updated!')
            return redirect('/')
        else:
            print("errors")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'foursquare/passwordchange.html', {
        'form': form
    })


class SearchQueryDelete(DeleteView):
    model = LocationSearch
    success_url = reverse_lazy('search')


def delete_user(request, pk):
    print(pk)
    user = get_object_or_404(User, id=pk)
    user.is_active = False
    user.save()
    return search(request)


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
            birthday_users = Profile.objects.filter(date_of_birth=date)
            for user in birthday_users:
                user_mail_addresses.append(user.user.email)
                print("email sent to birthday guy! :" + str(user.user.email))
        else:
            print("its no ones birthday")
    user_mail_addresses = list(set(user_mail_addresses))  # remove duplicates
    send_mail('hi', 'happy birthday!', 'from@example.com', user_mail_addresses)
    print("email sent to these guys: ")
    print(user_mail_addresses)


def get_user_searches(current_user):
    print("current user id: "+str(current_user.id))
    print(LocationSearch.objects.all())
    print(LocationSearch.objects.filter(searched_by=current_user))
    return LocationSearch.objects.filter(searched_by=current_user)


def get_sorted_list(venue_list):
    return sorted(venue_list, key=itemgetter('checkin_count'), reverse=True)


def get_total_results(data):
    data = data.json()
    try:
        total_results = data['response']['totalResults']
    except KeyError:
        total_results = 0
    return total_results


def get_venue_list(data):
    data = data.json()
    venue_list = []
    try:
        for item in data['response']['groups']:
            for groups in item['items']:
                name = groups.get('venue').get('name')
                phone_number = set_phone_number(groups)
                check_in_count = groups.get('venue', {}).get('stats').get('checkinsCount')
                venue = {'name': name, 'phone_number': phone_number, 'checkin_count': check_in_count}
                venue_list.append(venue)
    except KeyError:
        print("Bad values")
    print("selam")
    print(venue_list)
    print("venue list length: " + str(len(venue_list)))
    return venue_list


def set_phone_number(groups):
    phone_number = groups.get('venue', {}).get('contact').get('formattedPhone')
    if phone_number is None:
        phone_number = 'N/A'
    return phone_number


def get_recent_searches():
    return LocationSearch.objects.order_by('-search_date')[:10]


def get_and_save_the_obj(food, location, user):
    # search for the object in database, if it doesn't exist,
    # then create it, finally change its search_date to now,
    # so it will appear on top of the recent_searches list.
    try:
        search_obj = LocationSearch.objects.get(food=food, location=location)
        print(str(search_obj.search_date))
        search_obj.search_date = timezone.now()
        if user.is_anonymous():
            search_obj.searched_by = None
        else:
            print("User is not anonymous!")
            search_obj.searched_by = user
        search_obj.save()
        print(str(search_obj.search_date))
        print("test ???")
    except LocationSearch.DoesNotExist:
        search_obj = LocationSearch.objects.create(food=food, location=location, searched_by=user)
    except LocationSearch.MultipleObjectsReturned:
        print("object exists")
    finally:
        search_obj.search_date = timezone.now()
        recent_searches = LocationSearch.objects.order_by('-search_date')[:10]
        for obj in recent_searches:
            print("recent searches: " + obj.food + " " + obj.location + " " + str(obj.searched_by))
        return search_obj


def get_response(food, location, offset):
    url = 'https://api.foursquare.com/v2/venues/explore'
    params = dict(
        client_id='EWVGDNKMOOMNXCU1KMTPNYZRU11BLVTCTG2LGJ2F44UQA1K1',
        #client_id='V131V0IPODZOAI4DH0TXB0W1VF4R1QCAHASGHJI35D3KJLWK',
        client_secret='E4M0HFS3AYQDMHSZTGAN0NOFZJQ34ELBNOZW4H4FPYKTCRZG',
        #client_secret='L5RZFRA1K2KPH33H12BFD3MECOJKEBIJSLP14KXYRYW3A5AF',
        v='20170801',
        near=location,
        query=food,
        limit=10,
        offset=offset,
    )
    resp = requests.get(url=url, params=params)
    return resp


# def get_age(user):
#     print(user.profile.date_of_birth.month)
#     return timezone.now().year - user.profile.date_of_birth.year


# def it_is_birthday(user):
#     birthday = user.profile.date_of_birth
#     now = timezone.now()
#     if birthday.month == now.month and birthday.day == now.day:
#         return True
#     else:
#         return False
#

