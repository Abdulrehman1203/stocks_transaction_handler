from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('auth/login/', user_login, name='user_login'),
    path('register/', views.register, name='register'),
    path('adduser/', views.add_user, name='add user'),
    path('user/<str:username>/', views.get_user_by_username, name='user_by_username'),
    path('addstocks/', views.add_stock, name='add stocks'),
    path('stocks/<str:ticker>/', views.get_stock, name='get stocks by ticker'),
    path('all/stocks', views.get_all_stocks, name='all stocks'),
    path('addtransaction/', views.add_transaction, name='add transaction'),
    path('transactions/<str:username>/', views.get_transactions, name='get transactions by username'),
    path('transactions/<str:username>/<str:start_timestamp>/<str:end_timestamp>/', views.get_transactions_by_date),

]
