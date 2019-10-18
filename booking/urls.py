from django.urls import path
from django.urls import reverse_lazy, reverse
from . import views
app_name = 'booking'
urlpatterns = [
    path('home/', views.Home.as_view(), name='home'),
    path('home/<int:pk>', views.HotelDetails.as_view(), name='hotel_details'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('add/', views.HotelCreate.as_view(), name='hotel_add'),
    path('reservation/list/', views.ReservationListView.as_view(), name='reservation_list'),
    path('reservation/<int:hotel_id>/', views.ReservationCreate.as_view(), name='reservation_add'),
    path('profile/delete/<int:pk>/', views.ReservationDelete.as_view(), name='reservation_delete'),
    path('profile/add_opinion/<int:pk>/', views.OpinionCreate.as_view(), name='opinion_add'),
    path('profile/<int:pk>/', views.HotelStatistics.as_view(), name='hotel_statistics'),
    path('update_months/<int:hotel_id>', views.update_reservations, name='update_months'),
    path('notify_email/', views.notify_email, name='notify_email'),
    path('search/', views.update_hotels, name='update_hotels'),
]
