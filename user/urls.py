from django.urls import path
from .views import *
app_name = 'user'

urlpatterns = [
    path('register/', register),
    path('login/', login, name='login'),
    path('logout/', logout),
    path('info/', info),
    path('issue/', issue),
    path('password/', password),
    path('posted/', posted),
    path('history/', history),
    path('favorites/', favorites),
    path('ban/', ban),
]