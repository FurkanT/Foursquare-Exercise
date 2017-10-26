from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.forms.extras.widgets import SelectDateWidget
from django.dispatch import receiver
from django.db.models.signals import post_save


class LocationSearch(models.Model):
    food = models.CharField(max_length=100, )
    location = models.CharField(max_length=50, )
    search_date = models.DateTimeField(auto_now_add=True)
    offset = models.CharField(max_length=5, default=1)
    searched_by = models.ForeignKey(User, blank=True, null=True)

    def __str__(self):
        return self.food + " " + self.location + " " + str(self.searched_by)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='foursquare/images/', blank=True)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
