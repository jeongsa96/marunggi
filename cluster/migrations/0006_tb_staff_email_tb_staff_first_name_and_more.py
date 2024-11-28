# Generated by Django 5.1.3 on 2024-11-28 16:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cluster', '0005_tb_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='tb_staff',
            name='email',
            field=models.EmailField(default=None, max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='tb_staff',
            name='first_name',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AddField(
            model_name='tb_staff',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tb_staff',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tb_staff',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tb_staff',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='tb_staff',
            name='last_name',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AlterField(
            model_name='tb_staff',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tb_staff',
            name='id_akses',
            field=models.ForeignKey(choices=[(21, 'Dokter/Apoteker'), (22, 'Staff Administrasi')], on_delete=django.db.models.deletion.CASCADE, to='cluster.tb_akses'),
        ),
        migrations.AlterField(
            model_name='tb_staff',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
        migrations.AlterField(
            model_name='tb_staff',
            name='username',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
