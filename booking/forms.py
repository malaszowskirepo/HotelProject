from django.forms import ModelForm, Textarea
from django import forms
from django.contrib.auth.models import Permission
from pip._vendor.msgpack.fallback import xrange

from booking.models import HotelOwner, Reservation, Opinion
from django.contrib.auth.forms import UserCreationForm
from booking.widgets import MonthYearWidget


class RegistrationForm(UserCreationForm):

    class Meta:
        model = HotelOwner
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'phone_number',
                  'hasHotel',)

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.hasHotel = self.cleaned_data['hasHotel']

        user.save()

        if user.hasHotel:
            permission = Permission.objects.filter(codename='has_hotel').first()
            user.user_permissions.add(permission)
            user.save()

        if commit:
            user.save()

        return user


class ReservationForm(ModelForm):
    class Meta:
        model = Reservation
        fields = ['reservation_from',
                  'reservation_to',
                  'reservation_room_sgl_quantity',
                  'reservation_room_dbl_quantity',
                  'reservation_room_twin_quantity',
                  'reservation_room_tpl_quantity',
                  'reservation_room_qdbl_quantity',
                  'reservation_room_family_quantity',
                  'reservation_room_apartment_quantity',
                  ]
        widgets = {
            'reservation_from': forms.DateTimeInput(attrs={'class': 'datetime-input'}),
            'reservation_to': forms.DateTimeInput(attrs={'class': 'datetime-input'}),
        }


class OpinionForm(ModelForm):
    class Meta:
        model = Opinion
        exclude = ['opinion_to', 'opinion_date']
        widgets = {
            'opinion_content': Textarea(attrs={'cols': 80, 'rows': 20}),
        }


class MyForm(forms.Form):
    date = forms.DateField(
        required=False,
        widget=MonthYearWidget(years=xrange(2004, 2010))
    )
