from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.SignUp, name='register_seller'),
    path('create/', views.create_payment_link, name='create_payment_link'),
    path('link/<uuid:transaction_id>/', views.payment_link_detail, name='payment_link_detail'),
    path('pay/<uuid:transaction_id>/', views.payment_page, name='payment_page'),
    path('success/<uuid:transaction_id>/', views.payment_success, name='payment_success'),
    path('confirm/<uuid:transaction_id>/', views.confirm_delivery, name='confirm_delivery'),
    path('confirmed/', views.confirmation_success, name='confirmation_success'),
]