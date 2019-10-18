from django.contrib import admin
from . import models
admin.site.register(models.HotelOwner)
admin.site.register(models.Reservation)
admin.site.register(models.Opinion)
# Register your models here.
