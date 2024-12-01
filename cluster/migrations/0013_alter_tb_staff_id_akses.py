# Generated by Django 5.1.3 on 2024-11-29 10:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cluster', '0012_alter_tb_staff_id_akses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tb_staff',
            name='id_akses',
            field=models.ForeignKey(blank=True, choices=[(21, 'Dokter/Apoteker'), (22, 'Staff Administrasi'), (23, 'Admin')], null=True, on_delete=django.db.models.deletion.CASCADE, to='cluster.tb_akses'),
        ),
    ]