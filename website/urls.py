from django.urls import path
from . import views


app_name = 'website'


urlpatterns = [
    path('', views.CreateCard.as_view(), name='create-card'),
]
