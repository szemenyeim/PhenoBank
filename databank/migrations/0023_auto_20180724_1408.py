# Generated by Django 2.0.7 on 2018-07-24 12:08

import databank.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('databank', '0022_species_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='species',
            name='image',
            field=models.ImageField(null=True, upload_to=databank.models.upl_file_name_spec, verbose_name='Image'),
        ),
    ]
