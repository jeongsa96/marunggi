from django.urls import path
from . import views

urlpatterns = [
    path("", views.BASE, name="BASE"),
    path("kelola-user/<int:id>/", views.MANAGE_USER, name="kelola-user"),
    path("delete-user/<int:pk>/", views.DELETE_USER, name="delete-user"),
    path("kelola-data/", views.DATA, name="kelola-data"),
    path("hasil-cluster/", views.HASIL_CLUSTER, name="hasil-cluster")
]