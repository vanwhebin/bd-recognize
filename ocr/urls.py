# _*_ coding: utf-8 _*_
# @Time     :   2020/7/9 15:41
# @Author       vanwhebin

from django.urls import path

from . import views


urlpatterns = [
	path('api/invoice', views.invoice, name='invoice'),
]
