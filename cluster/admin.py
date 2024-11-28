from django.contrib import admin
from .models import tb_staff
from .models import tb_akses
from .models import tb_data

# Register your models here.
admin.site.register(tb_akses)
admin.site.register(tb_staff)
admin.site.register(tb_data)
