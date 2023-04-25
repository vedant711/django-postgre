from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('create',views.create),
    path('dashboard',views.dashboard),
    path('credit',views.credit),
    path('debit',views.debit),
    path('transfer',views.transfer),
    path('logout',views.logout_view),
]