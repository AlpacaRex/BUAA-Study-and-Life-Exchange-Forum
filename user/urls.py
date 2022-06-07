from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('logout/', logout),
    path('info/', info),
    path('issue/', issue),
    path('password/', password),
    path('posted/', posted),
    path('history/', history),
    path('favorites/', favorites),
]