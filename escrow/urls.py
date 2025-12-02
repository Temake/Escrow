from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.SignUp, name='register_seller'),
    path('login/', views.SignIn, name='signin'),
    path('logout/', views.SignOut, name='logout'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('create/', views.create_payment_link, name='create_payment_link'),
    path('link/<uuid:transaction_id>/', views.payment_link_detail, name='payment_link_detail'),
    path('pay/<uuid:transaction_id>/', views.payment_page, name='payment_page'),
    path('paystack/callback/', views.paystack_callback, name='paystack_callback'),
    path('success/<uuid:transaction_id>/', views.payment_success, name='payment_success'),
    path('confirm/<uuid:transaction_id>/', views.confirm_delivery, name='confirm_delivery'),
    path('confirmed/', views.confirmation_success, name='confirmation_success'),
]