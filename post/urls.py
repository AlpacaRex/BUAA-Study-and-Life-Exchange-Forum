from django.urls import path

from post.views import *


urlpatterns = [
    path('new/', new),
    path('comment/', comment),
    path('search/', search),
]