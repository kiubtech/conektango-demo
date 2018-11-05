from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('my-profile/', views.UserProfile.as_view(), name='my-profile'),
    path('conekta/account/create-or-delete', views.CreateOrDeleteConektaCustomer.as_view(),
         name='create-delete-conekta-account'),
    path('card/list/', views.CardList.as_view(), name='card-list'),
    path('card/add/', views.CreateCard.as_view(), name='card-add'),
    path('card/<str:card_id>/delete/', views.CardDelete.as_view(), name='card-delete'),
    # Payment-
    path('payments/add/', views.PaymentsAdd.as_view(), name='payments-add'),
]
