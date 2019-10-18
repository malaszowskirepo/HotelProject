from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMessage
from django.core.serializers import json
from django.forms.utils import ErrorList
from django.views.generic import TemplateView, ListView, CreateView, DeleteView, DetailView
from django.contrib.auth.urls import views as auth_views
from django.views import View
from booking.forms import RegistrationForm, ReservationForm, OpinionForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render, render_to_response
from .models import HotelOwner, Hotel, Reservation, ReservationDays, Opinion
from django.contrib.auth.models import Permission
from django.urls import reverse_lazy, reverse
from datetime import timedelta, date, datetime
from django import forms
import requests
import json
from statistics import mode
import pycountry

from django.shortcuts import get_object_or_404
from django.http.response import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

class Home(ListView):
    template_name = 'booking/home.html'
    context_object_name = 'all_hotels'

    def get_context_data(self, *, object_list=None, **kwargs):
        now = datetime.now()
        context = super().get_context_data(**kwargs)
        context['now'] = now.strftime("%Y-%m-%d")
        top_opinions = Opinion.objects.order_by('-opinion_rating')[:3]
        context['top_opinions'] = top_opinions
        return context

    def get_queryset(self):
        qs = Hotel.objects.all()
        # query = self.request.GET.get("q", None)
        # if query is not None:
        #     qs = qs.filter(hotel_city__icontains=query)
        # else:
        #     qs = Hotel.objects.all()

        return qs


class HotelCreate(CreateView):
    model = Hotel
    fields = ('hotel_name',
              'hotel_country',
              'hotel_city',
              'hotel_zip_code',
              'hotel_room_sgl',
              'hotel_room_dbl',
              'hotel_room_twin',
              'hotel_room_tpl',
              'hotel_room_qdbl',
              'hotel_room_family',
              'hotel_room_apartment',
              'hotel_room_sgl_price',
              'hotel_room_dbl_price',
              'hotel_room_twin_price',
              'hotel_room_tpl_price',
              'hotel_room_qdbl_price',
              'hotel_room_family_price',
              'hotel_room_apartment_price',
              'hotel_street',
              'hotel_street_number',
              'hotel_place_number',
              'hotel_short_desc',
              'hotel_long_desc',
              'hotel_image',
              )

    def get_success_url(self):
        return reverse('booking:profile')

    def form_valid(self, form):
        form.instance.hotel_owner = self.request.user
        form.save()
        return super(HotelCreate, self).form_valid(form)


class HotelDetails(DetailView):
    model = Hotel
    context_object_name = 'hotel'

    def get_context_data(self, **kwargs):
        context = super(HotelDetails, self).get_context_data(**kwargs)
        hotel = self.object
        # r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=Warsaw&APPID=7af3e1c13530a203c0072482e73166e3')
        # print(str(pycountry.countries.get(name='Poland').alpha_2).lower())

        weekday_list = []
        r = None
        if pycountry.countries.get(name=hotel.hotel_country) is not None:
            r = requests.get('http://api.openweathermap.org/data/2.5/forecast?q={0},{1}&units=metric&APPID=7af3e1c13530a203c0072482e73166e3'.format(hotel.hotel_city, pycountry.countries.get(name=hotel.hotel_country).alpha_2.lower()))

            json_data = json.loads(r.text)
            icon_links_list = []
            for day in json_data['list']:
                icon_links_list.append('http://openweathermap.org/img/w/{0}.png'.format(day['weather'][0]['icon']))

            min_temps_list_full = []
            max_temps_list_full = []
            for day in json_data['list']:
                min_temps_list_full.append(day['main']['temp_min'])
                max_temps_list_full.append(day['main']['temp_max'])

            min_temps_list = ['%.1f' % e for e in min_temps_list_full]
            max_temps_list = ['%.1f' % e for e in max_temps_list_full]

            # print(min(min_temps_list[0:8]))
            # print(max(max_temps_list[0:8]))

            weather_main_list_full = []
            for day in json_data['list']:
                weather_main_list_full.append(day['weather'][0]['main'])

            weather_main_list = [e.lower() for e in weather_main_list_full]


            for i in range(0, 5):
                weekday_list.append('{0}({1})'.format(((datetime.now() + timedelta(days=i)).strftime("%d.%m")), (datetime.now() + timedelta(days=i)).strftime("%A")))

            context['icon_day1_links_list'] = icon_links_list[0:8]
            context['icon_day2_links_list'] = icon_links_list[8:16]
            context['icon_day3_links_list'] = icon_links_list[16:24]
            context['icon_day4_links_list'] = icon_links_list[24:32]
            context['icon_day5_links_list'] = icon_links_list[32:40]
            context['day1desc'] = most_common(weather_main_list[0:8])
            context['day2desc'] = most_common(weather_main_list[8:16])
            context['day3desc'] = most_common(weather_main_list[16:24])
            context['day4desc'] = most_common(weather_main_list[24:32])
            context['day5desc'] = most_common(weather_main_list[32:40])
            context['min_temp_day_1'] = min(min_temps_list[0:8])
            context['min_temp_day_2'] = min(min_temps_list[8:16])
            context['min_temp_day_3'] = min(min_temps_list[16:24])
            context['min_temp_day_4'] = min(min_temps_list[24:32])
            context['min_temp_day_5'] = min(min_temps_list[32:40])
            context['max_temp_day_1'] = max(max_temps_list[0:8])
            context['max_temp_day_2'] = max(max_temps_list[8:16])
            context['max_temp_day_3'] = max(max_temps_list[16:24])
            context['max_temp_day_4'] = max(max_temps_list[24:32])
            context['max_temp_day_5'] = max(max_temps_list[32:40])
            context['weekday_list'] = weekday_list

        hotel_rating_rounded = round(self.object.hotel_rating)
        opinions_to_hotel = Opinion.objects.filter(opinion_to__reservation_hotel=self.object)
        opinions_to_hotel_count = opinions_to_hotel.count()
        context['opinions'] = Opinion.objects.filter(opinion_to__reservation_hotel=self.object)
        context['hotel_rating_rounded'] = hotel_rating_rounded
        context['hotel_rating_left'] = 5 - hotel_rating_rounded
        context['opinions_to_hotel_count'] = opinions_to_hotel_count

        return context


def most_common(lst):
    return max(set(lst), key=lst.count)


class HotelStatistics(ListView):
    context_object_name = 'reservations'
    template_name = 'booking/hotel_statistics.html'

    def get_queryset(self, **kwargs):
        pknum = self.kwargs.get('pk', )
        hotel = Hotel.objects.get(pk=pknum)
        reservationsDuringMonth = Reservation.objects.filter(reservation_hotel=hotel).filter(reservation_from__month=datetime.now().month).order_by('reservation_from')
        return reservationsDuringMonth

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HotelStatistics, self).get_context_data(**kwargs)
        pknum = self.kwargs.get('pk', )
        hotel = Hotel.objects.get(pk=pknum)
        context['hotel_id'] = hotel.pk
        context['hotel'] = hotel
        return context


@csrf_exempt
def update_months(request, hotel_id):
    if request.GET.get('month'):
        month = request.GET.get('month')
        request.session['month'] = int(month) + 1
        return HttpResponseRedirect(reverse('booking:hotel_statistics', args=(hotel_id,)))
    else:
        return render_to_response(request, 'booking/hotel_statistics.html')




class ReservationCreate(CreateView):
    form_class = ReservationForm
    model = Reservation
    success_url = reverse_lazy('booking:home')

    def form_valid(self, form, **kwargs):
        pknum = self.kwargs.get('hotel_id', )
        hotel = Hotel.objects.get(pk=pknum)
        form.instance.reservation_hotel = hotel
        form.instance.reservation_owner = self.request.user

        start_date = form.instance.reservation_from
        end_date = form.instance.reservation_to
        today = date.today()
        start_date.strftime('%m-%d-%y')
        end_date.strftime('%m-%d-%y')


        sgl_room_quantity = 0
        dbl_room_quantity = 0
        twin_room_quantity = 0
        tpl_room_quantity = 0
        qdbl_room_quantity = 0
        family_room_quantity = 0
        apartment_room_quantity = 0

        # hotel_room_sgl
        room_sgl_error = False
        if form.instance.reservation_room_sgl_quantity > 0:
            sgl_room_quantity = form.instance.reservation_room_sgl_quantity
            room_sgl_error = error_validation(sgl_room_quantity, hotel, 'hotel_room_sgl', hotel.hotel_room_sgl,
                                              start_date, end_date)

        room_dbl_error = False
        if form.instance.reservation_room_dbl_quantity > 0:
            dbl_room_quantity = form.instance.reservation_room_dbl_quantity
            room_dbl_error = error_validation(dbl_room_quantity, hotel, 'hotel_room_dbl', hotel.hotel_room_dbl,
                                              start_date, end_date)

        room_twin_error = False
        if form.instance.reservation_room_twin_quantity > 0:
            twin_room_quantity = form.instance.reservation_room_twin_quantity
            room_twin_error = error_validation(twin_room_quantity, hotel, 'hotel_room_twin', hotel.hotel_room_twin,
                                               start_date, end_date)

        room_tpl_error = False
        if form.instance.reservation_room_tpl_quantity > 0:
            tpl_room_quantity = form.instance.reservation_room_tpl_quantity
            room_tpl_error = error_validation(tpl_room_quantity, hotel, 'hotel_room_tpl', hotel.hotel_room_tpl,
                                              start_date, end_date)

        room_qdbl_error = False
        if form.instance.reservation_room_qdbl_quantity > 0:
            qdbl_room_quantity = form.instance.reservation_room_qdbl_quantity
            room_qdbl_error = error_validation(qdbl_room_quantity, hotel, 'hotel_room_qdbl', hotel.hotel_room_qdbl,
                                               start_date,
                                               end_date)

        room_family_error = False
        if form.instance.reservation_room_family_quantity > 0:
            family_room_quantity = form.instance.reservation_room_family_quantity
            room_family_error = error_validation(family_room_quantity, hotel, 'hotel_room_family',
                                                 hotel.hotel_room_family, start_date,
                                                 end_date)

        room_apartment_error = False
        if form.instance.reservation_room_apartment_quantity > 0:
            apartment_room_quantity = form.instance.reservation_room_apartment_quantity
            room_apartment_error = error_validation(apartment_room_quantity, hotel, 'hotel_room_apartment',
                                                    hotel.hotel_room_apartment,
                                                    start_date, end_date)

        date_error = False
        date_error_2 = False

        if end_date < start_date:
            date_error = True

        print("start date: " + str(start_date))
        print("end date: " + str(end_date))
        print("today: " + str(today))

        if start_date < today or end_date < today:
            date_error_2 = True

        zero_quantity_error = False
        if sgl_room_quantity == 0 and dbl_room_quantity == 0 and twin_room_quantity == 0 and tpl_room_quantity == 0 and \
                qdbl_room_quantity == 0 and family_room_quantity == 0 and apartment_room_quantity == 0:
            zero_quantity_error = True

        print("room_sgl_error: " + str(room_sgl_error) + " room_dbl_error: " +
              str(room_dbl_error) + " room_twin_error: " + str(room_twin_error) +
              " room_tpl_error: " + str(room_tpl_error) + " room_qdbl_error: " + str(room_qdbl_error) +
              " room_family_error: " + str(room_family_error) + " room_apartment_error: " + str(room_apartment_error) +
              " date_error: " + str(date_error) + " date_error_2: " + str(date_error_2) + " zero_quantity_error: "
              + str(zero_quantity_error))

        if room_sgl_error or room_dbl_error or room_twin_error or room_tpl_error or room_qdbl_error or \
                room_family_error or room_apartment_error or date_error or date_error_2 or zero_quantity_error:

            print("weszlo do bledow")
            if date_error:
                form.add_error('reservation_from', forms.ValidationError('End date must be greater then start date'))
                form.add_error('reservation_to', forms.ValidationError('End date must be greater then start date'))
            if date_error_2:
                form.add_error('reservation_from', forms.ValidationError('You cant choose a date earlier than today.'))
                form.add_error('reservation_to', forms.ValidationError('You cant choose a date earlier than today.'))
            return super(ReservationCreate, self).form_invalid(form)
        else:

            form.instance.reservation_total_price = sgl_room_quantity * hotel.hotel_room_sgl_price + \
                                                    dbl_room_quantity * hotel.hotel_room_dbl_price + \
                                                    twin_room_quantity * hotel.hotel_room_twin_price + \
                                                    tpl_room_quantity * hotel.hotel_room_tpl_price + \
                                                    qdbl_room_quantity * hotel.hotel_room_qdbl_price + \
                                                    family_room_quantity * hotel.hotel_room_family_price + \
                                                    apartment_room_quantity * hotel.hotel_room_apartment_price

            response = super(ReservationCreate, self).form_valid(form)
            if start_date != end_date:
                for single_date in daterange(start_date, end_date):
                    if sgl_room_quantity > 0:
                        for i in range(sgl_room_quantity):
                            ReservationDays.objects.create(reservation=form.instance, reservation_dates=single_date
                                                           , reservation_room='hotel_room_sgl', )
                    if dbl_room_quantity > 0:
                        for i in range(dbl_room_quantity):
                            ReservationDays.objects.create(reservation=form.instance, reservation_dates=single_date
                                                           , reservation_room='hotel_room_dbl', )
                    if twin_room_quantity > 0:
                        for i in range(twin_room_quantity):
                            ReservationDays.objects.create(reservation=form.instance, reservation_dates=single_date
                                                           , reservation_room='hotel_room_twin', )
                    if tpl_room_quantity > 0:
                        for i in range(tpl_room_quantity):
                            ReservationDays.objects.create(reservation=form.instance, reservation_dates=single_date
                                                           , reservation_room='hotel_room_tpl', )
                    if qdbl_room_quantity > 0:
                        for i in range(qdbl_room_quantity):
                            ReservationDays.objects.create(reservation=form.instance, reservation_dates=single_date
                                                           , reservation_room='hotel_room_qdbl', )
                    if family_room_quantity > 0:
                        for i in range(family_room_quantity):
                            ReservationDays.objects.create(reservation=form.instance, reservation_dates=single_date
                                                           , reservation_room='hotel_room_family', )
                    if apartment_room_quantity > 0:
                        for i in range(apartment_room_quantity):
                            ReservationDays.objects.create(reservation=form.instance, reservation_dates=single_date
                                                           , reservation_room='hotel_room_apartment', )
            else:
                if sgl_room_quantity > 0:
                    for i in range(sgl_room_quantity):
                        ReservationDays.objects.create(reservation=form.instance, reservation_dates=start_date,
                                                       reservation_room='hotel_room_sgl', )
                if dbl_room_quantity > 0:
                    for i in range(dbl_room_quantity):
                        ReservationDays.objects.create(reservation=form.instance, reservation_dates=start_date,
                                                       reservation_room='hotel_room_dbl', )
                if twin_room_quantity > 0:
                    for i in range(twin_room_quantity):
                        ReservationDays.objects.create(reservation=form.instance, reservation_dates=start_date,
                                                       reservation_room='hotel_room_twin', )
                if tpl_room_quantity > 0:
                    for i in range(tpl_room_quantity):
                        ReservationDays.objects.create(reservation=form.instance, reservation_dates=start_date,
                                                       reservation_room='hotel_room_tpl', )
                if qdbl_room_quantity > 0:
                    for i in range(qdbl_room_quantity):
                        ReservationDays.objects.create(reservation=form.instance, reservation_dates=start_date,
                                                       reservation_room='hotel_room_qdbl', )
                if family_room_quantity > 0:
                    for i in range(family_room_quantity):
                        ReservationDays.objects.create(reservation=form.instance, reservation_dates=start_date,
                                                       reservation_room='hotel_room_family', )
                if apartment_room_quantity > 0:
                    for i in range(apartment_room_quantity):
                        ReservationDays.objects.create(reservation=form.instance, reservation_dates=start_date,
                                                       reservation_room='hotel_room_apartment', )

            thisReservationDays = ReservationDays.objects.filter(reservation=form.instance)
            for day in thisReservationDays:
                print(str(day.reservation_dates) + " - " + day.reservation_room)


            return response


def error_validation(room_quantity_from_form, hotel, hotel_room_str, hotel_room_quantity, start_date, end_date):
    reservation_days = ReservationDays.objects.filter(reservation_room=hotel_room_str,
                                                      reservation__reservation_hotel=hotel)
    for single_date in daterange(start_date, end_date):
        counter = reservation_days.filter(reservation_dates=single_date).count()
        if room_quantity_from_form > hotel_room_quantity - counter or room_quantity_from_form > hotel_room_quantity:
            return True
        else:
            return False


class OpinionCreate(CreateView):
    form_class = OpinionForm
    model = Opinion
    success_url = reverse_lazy('booking:profile')

    def form_valid(self, form, **kwargs):
        reservation_pk = self.kwargs.get('pk', )
        reservation = Reservation.objects.get(pk=reservation_pk)
        form.instance.opinion_to = reservation
        form.instance.opinion_date = date.today()
        count = Opinion.objects.filter(opinion_to=reservation).count()
        reservation_end_date = reservation.reservation_to
        opinion_form = form.save(commit=False)

        if count == 1 or reservation_end_date >= date.today():
            return redirect(reverse('booking:profile'))
        else:
            opinion_form.save()
            hotel = Hotel.objects.get(pk=reservation.reservation_hotel.id)
            opinions_to_hotel = Opinion.objects.filter(opinion_to__reservation_hotel=hotel)
            opinions_to_hotel_count = opinions_to_hotel.count()
            rating_sum = 0.0
            hotel_rating_value = 0.0
            for opinion_to_hotel in opinions_to_hotel:
                rating_sum = rating_sum + opinion_to_hotel.opinion_rating
            if opinions_to_hotel_count > 0:
                hotel_rating_value = rating_sum / opinions_to_hotel_count
            else:
                hotel.hotel_rating = 0.0

            Hotel.objects.filter(pk=reservation.reservation_hotel.id).update(hotel_rating=hotel_rating_value)
            return super().form_valid(form)


class ReservationDelete(DeleteView):
    model = Reservation
    template_name = 'booking/delete_reservation.html'

    def delete(self, request, *args, **kwargs):
        success_url = self.get_success_url()
        obj = super(ReservationDelete, self).get_object()
        now = datetime.datetime.now() + datetime.timedelta(days=-1)
        if obj.reservation_from.strftime("%Y-%m-%d") > now.strftime("%Y-%m-%d"):
            if self.request.method == "POST":
                explanation_text = self.request.POST.get("info", None)
                email = EmailMessage('Your reservation was deleted, cheers.',
                                     explanation_text, to=[obj.reservation_hotel.hotel_owner.email])
                #email.send()
                print("post")
            if self.request.method == "GET":
                print("get")
            return super(ReservationDelete, self).delete(request, *args, **kwargs)
        else:
            print("mamy problem")
            return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('booking:profile')


class Profile(ListView):
    template_name = 'booking/profile.html'
    context_object_name = 'my_reservations_or_hotels'

    def get_queryset(self):
        if self.request.user.hasHotel:
            return Hotel.objects.filter(hotel_owner=self.request.user)
        else:
            return Reservation.objects.filter(reservation_owner=self.request.user)


class LoginUserView(auth_views.LoginView):
    template_name = 'booking/login.html'


class LogoutUserView(auth_views.LogoutView):
    template_name = 'booking/logout.html'


class ReservationListView(ListView):
    context_object_name = 'all_reservations'

    def get_queryset(self):
        return Reservation.objects.all()


class RegisterUserView(View):
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booking:login')
        else:
            return redirect('booking:register')

    def get(self, request):
        form = RegistrationForm()
        args = {'form': form}
        return render(request, 'booking/reg_form.html', args)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)
    yield end_date

def hello(request):
    return HttpResponse('Hello World!')

@csrf_exempt
def update_hotels(request):
    search_text = request.POST['search_text']
    all_hotels = Hotel.objects.filter(hotel_city__icontains=search_text)
    print("all_hotels.count(): " + str(all_hotels.count()))
    print(search_text)
    for hotel in all_hotels:
        print(str(hotel.hotel_name))
    return render(request, 'booking/ajax_search.html', {'all_hotels': all_hotels})


@csrf_exempt
def update_reservations(request, hotel_id):
    month_search = request.POST['month']
    hotel = Hotel.objects.get(pk=hotel_id)
    reservationsDuringMonth = Reservation.objects.filter(reservation_from__month=month_search)\
        .filter(reservation_hotel=hotel).order_by('reservation_from')
    return render(request, 'booking/ajax_reservation_search.html', {'reservations': reservationsDuringMonth,
                                                                    'hotel': hotel})


# @csrf_exempt
# def update_reservations(request, hotel_id):
#     month_search = request.POST['month']
#     hotel = Hotel.objects.get(pk=hotel_id)
#     print("tu sprawdzamy: " + str(month_search))
#     print("hotel: " + hotel.hotel_name)
#     reservationsDuringMonth = Reservation.objects.filter(reservation_from__month=month_search)\
#         .filter(reservation_hotel=hotel).order_by('reservation_from')
#     for reservation in reservationsDuringMonth:
#         print("reservation: " + str(reservation.reservation_from))
#     print("month " + month_search)
#     print("reservationsDuringMonth count: " + str(reservationsDuringMonth.count()))
#     return render(request, 'booking/ajax_reservation_search.html', {'reservations': reservationsDuringMonth,
#                                                                     'hotel': hotel})

def notify_email(request):
    email = EmailMessage('title', 'body', to=['malaszowski@interia.pl'])
    email.send()
    return render(request, 'booking/home.html')
