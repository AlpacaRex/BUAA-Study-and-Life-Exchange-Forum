from django.urls import path

from post.views import *


urlpatterns = [
    path('new/', new),
    path('comment/', comment),
    path('search/', search),
    path('browse/', browse),
    path('like/', like),
    path('delete/', delete)
]