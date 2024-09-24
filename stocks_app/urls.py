from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('register/', User_RegisterView.as_view(), name='register'),
    path('login/', User_LoginView.as_view(), name='login'),
    path('add-user/', Add_UserView.as_view(), name='add_user'),
    path('user/<str:username>/', GetUser_ByUsernameView.as_view(), name='get_user_by_username'),
    path('add-stock/', Add_StockView.as_view(), name='add_stock'),
    path('stock/<str:ticker>/', Get_StockView.as_view(), name='get_stock'),
    path('stocks/', Get_AllStocksView.as_view(), name='get_all_stocks'),
    path('add-transaction/', Add_TransactionView.as_view(), name='add_transaction'),
    path('transactions/<str:username>/<str:start_time>/<str:end_time>/', Get_TransactionsByDateView.as_view()),
    path('transactions/<str:username>/', Get_TransactionsView.as_view(), name='get_transactions')
]
