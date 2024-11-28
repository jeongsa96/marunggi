from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class tb_akses(models.Model):
    id_akses = models.IntegerField(primary_key=True)
    nama_akses = models.CharField(max_length=25)

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

class tb_staffManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not username:
            raise ValueError('Inputkan username anda')
        
        if not email:
            raise ValueError('Inputkan email anda')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,           
            first_name = first_name,
            last_name = last_name,
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)

class tb_staff(AbstractBaseUser):    
    DOKTERAPOTEKER = 21
    STAFF_ADMINISTRASI = 22

    ROLE_CHOICE = (
        (DOKTERAPOTEKER, 'Dokter/Apoteker'),
        (STAFF_ADMINISTRASI, 'Staff Administrasi'),
    )

    first_name = models.CharField(max_length=50, default=None)
    last_name = models.CharField(max_length=50, default=None)
    email = models.EmailField(max_length=100, unique=True, default=None)
    username = models.CharField(max_length=50,unique=True)
    id_akses = models.ForeignKey(tb_akses, choices=ROLE_CHOICE, on_delete=models.CASCADE, blank=False, null=False)
    # require fields
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','first_name','last_name']

    objects = tb_staffManager()

    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return True


