from django.db import models

class tb_akses(models.Model):
    id_akses = models.IntegerField(primary_key=True)
    nama_akses = models.CharField(max_length=25)

class tb_staff(models.Model):
    id = models.IntegerField(primary_key=True)
    id_akses = models.ForeignKey(tb_akses, on_delete=models.CASCADE)
    username = models.CharField(max_length=25)
    password = models.CharField(max_length=50)

class tb_data(models.Model):
    id_data = models.IntegerField(primary_key=True)    
    nama_penyakit = models.CharField(max_length=100)
    tanggal_input = models.DateField()
    r1 = models.IntegerField()
    r2 = models.IntegerField()
    r3 = models.IntegerField()
    r4 = models.IntegerField()
    r5 = models.IntegerField()
    r6 = models.IntegerField()
    r7 = models.IntegerField()
    r8 = models.IntegerField()
    r9 = models.IntegerField()
    r10 = models.IntegerField()
    r11 = models.IntegerField()
    r12 = models.IntegerField()
    total = models.IntegerField()


