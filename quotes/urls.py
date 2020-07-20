from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('transactions.html', views.transactions, name="transactions"),
    path('add_stock.html', views.add_stock, name="add_stock"),
    path('delete/<stock_id>', views.delete, name="delete"),
    path('reset_portfolio', views.reset_portfolio, name="reset_portfolio"),
    path('delete_stock.html', views.delete_stock, name="delete_stock"),
]