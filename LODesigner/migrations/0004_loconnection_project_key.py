# Generated by Django 4.2.3 on 2023-07-28 01:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LODesigner', '0003_locircuit_loconnection_lodevice'),
    ]

    operations = [
        migrations.AddField(
            model_name='loconnection',
            name='project_key',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='LODesigner.project'),
        ),
    ]
