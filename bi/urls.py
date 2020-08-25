# _*_ coding: utf-8 _*_
# @Time     :   2020/8/21 11:43
# @Author       vanwhebin
from django.urls import path

from . import views


urlpatterns = [
	path('sales-data', views.sales_data, name='sales_data'),
	path('sales-brand', views.sales_brand, name='sales_brand'),
	path('sales-team', views.sales_team, name='sales_team'),
]
