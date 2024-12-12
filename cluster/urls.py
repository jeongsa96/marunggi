from django.urls import path
from . import views

urlpatterns = [
    path("", views.HOME, name="halaman-home"),
    path("login/", views.LOGIN, name="login"),
    path("kelola-user/<int:id>/", views.MANAGE_USER, name="kelola-user"),
    path("delete-user/<int:pk>/", views.DELETE_USER, name="delete-user"),
    path("kelola-data/", views.DATA, name="kelola-data"),
    path("hasil-cluster/", views.HASIL_CLUSTER, name="hasil-cluster"),                                                                                                                              
    path("hasil-prediksi/", views.HASIL_PREDIKSI, name="hasil-prediksi")
]