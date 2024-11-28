from django.urls import path
from . import views

urlpatterns = [
    path("", views.BASE, name="BASE"),
    path("kelola-data/", views.DATA, name="KELOLA DATA"),
]