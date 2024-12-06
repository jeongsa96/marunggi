from django.db import models

class tb_akses(models.Model):
    id_akses = models.IntegerField(primary_key=True)
    nama_akses = models.CharField(max_length=25)

class tb_data(models.Model):
    id_data = models.IntegerField(primary_key=True)    
    nama_penyakit = models.CharField(max_length=100)
    tanggal_input = models.DateField(null=False)
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

class tb_staff(models.Model):    
    email = models.EmailField(max_length=100, unique=True, default=None)
    username = models.CharField(max_length=50,unique=True)
    password = models.CharField(max_length=100)
    id_akses = models.ForeignKey(tb_akses, on_delete=models.CASCADE, default=None)

class tb_jenis_penyakit(models.Model):
    id_jenis_penyakit = models.IntegerField(primary_key=True)
    nama_jenis_penyakit = models.CharField(max_length=255)

class tb_penyakit(models.Model):
    id_penyakit = models.IntegerField(primary_key=True)
    id_jenis_penyakit = models.ForeignKey(tb_jenis_penyakit, on_delete=models.CASCADE, default=None)
    nama_penyakit = models.CharField(max_length=255)

class tb_hasil_cluster(models.Model):
    nama_penyakit = models.CharField(max_length=255)
    tanggal = models.DateField(null=False)
    hasil_klasifikasi = models.CharField(max_length=50)

    
    
    

