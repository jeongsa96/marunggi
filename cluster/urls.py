from django.urls import path
from . import views

urlpatterns = [
    path("", views.BASE, name="BASE"),
    path("kelola-data/", views.DATA, name="KELOLA DATA"),
    path("kelola-user/", views.MANAGE_USER, name="KELOLA USER"),
    path("delete-user/<int:pk>/", views.DELETE_USER, name="HAPUS USER"),
]