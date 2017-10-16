from django.db import models


class LocationSearch(models.Model):
    food = models.CharField(max_length=100, default='', blank=True)
    location = models.CharField(max_length=50, default='', blank=True)
    search_date = models.DateTimeField('search_date', auto_now_add=True)

    # def __str__(self):
    # return self.food +" in "+ self.location
