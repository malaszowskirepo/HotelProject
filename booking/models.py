from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from datetime import datetime
import datetime
from django.core.validators import RegexValidator
from django.forms import DateTimeInput
from django.db.models.signals import post_save
from django.dispatch import receiver


class HotelOwner(AbstractUser):

    hasHotel = models.BooleanField(default=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits "
                                         "allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False, null=False)

    class Meta:
        app_label = 'booking'
        permissions = ("has_hotel", "Has hotel."),


class Hotel(models.Model):
    hotel_owner = models.ForeignKey(HotelOwner, on_delete=models.CASCADE)
    hotel_name = models.CharField(max_length=120, verbose_name="Your hotel name")
    hotel_country = models.CharField(max_length=50, verbose_name="Your hotel country")
    hotel_city = models.CharField(max_length=100, verbose_name="Your hotel city")
    hotel_zip_code = models.CharField(max_length=6, default="43-701", verbose_name="Your hotel zip code")
    hotel_street = models.CharField(max_length=100, verbose_name="Your hotel street")
    hotel_street_number = models.IntegerField(default=0, verbose_name="Your hotel street number")
    hotel_place_number = models.IntegerField(default=0, verbose_name="Your hotel place number")
    hotel_short_desc = models.TextField(max_length=200, verbose_name="Briefly describe your hotel")
    hotel_long_desc = models.TextField(max_length=2000, verbose_name="Full description of your hotel")
    hotel_image = models.FileField(verbose_name="Upload image with your hotel")
    hotel_rating = models.FloatField(default=0.0)

    hotel_room_sgl = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                 verbose_name="Number of single rooms in your hotel")
    hotel_room_dbl = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                 verbose_name="Number of double rooms in your hotel")
    hotel_room_twin = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                  verbose_name="Number of twin rooms in your hotel")
    hotel_room_tpl = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                 verbose_name="Number of triple rooms in your hotel")
    hotel_room_qdbl = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                  verbose_name="Number of quad rooms in your hotel")
    hotel_room_family = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                    verbose_name="Number of family rooms in your hotel")
    hotel_room_apartment = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                       verbose_name="Number of apartment rooms in your hotel")

    hotel_room_sgl_price = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                       verbose_name="Your hotel single room price in $")
    hotel_room_dbl_price = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                       verbose_name="Your hotel double room price in $")
    hotel_room_twin_price = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                        verbose_name="Your hotel twin room price in $")
    hotel_room_tpl_price = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                       verbose_name="Your hotel triple room price in $")
    hotel_room_qdbl_price = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                        verbose_name="Your hotel quad room price in $")
    hotel_room_family_price = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                          verbose_name="Your hotel family room price in $")
    hotel_room_apartment_price = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0,
                                                             verbose_name="Your hotel apartment room price in $")

    @property
    def rating(self):
        hotel_rating_rounded = round(self.hotel_rating)
        return hotel_rating_rounded

    @property
    def rating_left(self):
        hotel_rating_rounded = round(self.hotel_rating)
        return 5 - hotel_rating_rounded

    def __str__(self):
        return self.hotel_name


class Reservation(models.Model):
    reservation_owner = models.ForeignKey(HotelOwner, on_delete=models.CASCADE)
    reservation_hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    reservation_from = models.DateField()
    reservation_to = models.DateField()
    reservation_room_sgl_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    reservation_room_dbl_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    reservation_room_twin_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    reservation_room_tpl_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    reservation_room_qdbl_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    reservation_room_family_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    reservation_room_apartment_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    reservation_total_price = models.FloatField(default=0.0)

    @property
    def is_before(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d") < self.reservation_from.strftime("%Y-%m-%d")

    @property
    def is_after(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d") > self.reservation_to.strftime("%Y-%m-%d")

    @property
    def has_opinion(self):
        opinion = Opinion.objects.filter(opinion_to=self)
        count = opinion.count()
        return count == 1


class ReservationDays(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    reservation_room = models.CharField(max_length=100)
    reservation_dates = models.DateField()

    def __str__(self):
        return str(self.reservation_dates)


class Opinion(models.Model):
    OPINION_CHOICES = (
        (0.0, 'Very Bad'),
        (1.0, 'Badly'),
        (2.0, 'Moderation'),
        (3.0, 'Good'),
        (4.0, 'Very Good'),
        (5.0, 'Excellent'),
    )
    opinion_to = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    opinion_date = models.DateField()
    opinion_content = models.TextField()
    opinion_rating = models.FloatField(blank=False, choices=OPINION_CHOICES)

    @property
    def rating_int(self):
        return int(self.opinion_rating)

    @property
    def rating_int_left(self):
        return 5 - int(self.opinion_rating)
