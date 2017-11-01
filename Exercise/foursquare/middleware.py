from django.utils import timezone
from django.shortcuts import render


class CheckBirthdayMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not request.user.is_authenticated():
            return response
        current_user = request.user
        birthday = current_user.profile.date_of_birth
        now = timezone.now()
        if birthday is not None:
            age = now.year - birthday.year
            if birthday.month == now.month and birthday.day == now.day:
                context = {
                    'user_name': current_user.username,
                    'age': age,
                }
                return render(request, "foursquare/birthdaypage.html", context)
        return response


