from django.contrib import admin
from .models import tb_staff
from .models import tb_akses
from .models import tb_data
from .models import tb_penyakit
from .models import tb_jenis_penyakit

# Register your models here.
admin.site.register(tb_akses)
admin.site.register(tb_staff)
admin.site.register(tb_data)
admin.site.register(tb_penyakit)
admin.site.register(tb_jenis_penyakit)
