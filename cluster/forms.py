from django import forms
from .models import tb_staff

class CreateForm(forms.ModelForm):
    class Meta:
        model = tb_staff
        fields = ('id_akses','username','password')

    