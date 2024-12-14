from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.LOGIN, name="login"),
    path("logout/", views.LOGOUT, name="logout"),
    path("", views.HOME, name="halaman-home"),
    path("kelola-user/<int:id>/", views.MANAGE_USER, name="kelola-user"),
    path("delete-user/<int:pk>/", views.DELETE_USER, name="delete-user"),
    path("kelola-data/", views.DATA, name="kelola-data"),
    path("hasil-cluster/", views.HASIL_CLUSTER, name="hasil-cluster"),                                                                                                                              
    path("hasil-prediksi/", views.HASIL_PREDIKSI, name="hasil-prediksi"),
    path("dokteker/", views.DOKTER_APOTEKER, name="dokteker"),
    path("dokteker/hasil-cluster", views.DA_HASIL_CLUSTER, name="da-cluster"),
    path("dokteker/hasil-prediksi", views.DA_HASIL_PREDIKSI, name="da-prediksi"),
    path("administrasi/", views.ADMINISTRASI, name="administrasi"),
    path("administrasi/kelola-data", views.SA_DATA, name="sa-data"),
    path("administrasi/hasil-cluster", views.SA_HASIL_CLUSTER, name="sa-cluster"),
    path("administrasi/hasil-prediksi", views.SA_HASIL_PREDIKSI, name="sa-prediksi"),
]