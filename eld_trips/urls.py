# eld_trips/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/trip/', views.trip_api, name='trip_api'),
]