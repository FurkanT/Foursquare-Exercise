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
from django.contrib import messages


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
    print("User: " + str(request.user))
    current_user = request.user
    if not current_user.is_anonymous():
        user_searches = get_user_searches(current_user)
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
        previous_offset = None
    else:
        previous_offset = int(offset) - 10
        if previous_offset == 0:        # this means if offset = 10, so in second page i want to show "previous"
            previous_offset = str(0)    # but if i don't make it a string prev_offset will be recognized as None
    if int(offset) >= total_results - 10:
        next_offset = None
    else:
        next_offset = int(offset) + 10
    context = {
        'venue_list': sorted_list,
        'recent_searches': recent_searches,
        'form_box': form,
        'next_offset': next_offset,
        'prev_offset': previous_offset,
        'current_search': current_search,
        'total_venue_count': total_results,
        'user_searches': user_searches,
        'user.profile.avatar': get_user_profile(request.user)
    }
    return render(request, 'foursquare/maintemp.html', context)


def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data.get("new_email")
            if not User.objects.filter(email=new_email) and new_email is not None:
                request.user.email = new_email
                request.user.save()
                messages.success(request, 'Your email has been updated successfully!')
                print("mail is now: "+str(request.user.email))
                return render(request, 'foursquare/emailchangepage.html', {'messages': messages.get_messages(request),
                                                                           'form': form})
            raise forms.ValidationError('This email address is already in use.')
        else:
            messages.warning(request, 'Please try again.')
            print("mail form is not valid")
            return render(request, 'foursquare/emailchangepage.html', {'messages': messages.get_messages(request)})
    else:
        form = ChangeEmailForm()
        return render(request, 'foursquare/emailchangepage.html', {'form': form})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
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
    if user.is_anonymous():
        user = None
    try:
        search_obj = LocationSearch.objects.get(food=food, location=location)
        print(str(search_obj.search_date))
        search_obj.search_date = timezone.now()
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
        client_secret='E4M0HFS3AYQDMHSZTGAN0NOFZJQ34ELBNOZW4H4FPYKTCRZG',
        v='20170801',
        near=location,
        query=food,
        limit=10,
        offset=offset,
    )
    resp = requests.get(url=url, params=params)
    return resp


def get_user_profile(user):
    if user.is_anonymous():
        return None
    return user.profile.avatar

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

