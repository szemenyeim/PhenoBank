# Generated by Django 2.0.5 on 2018-07-04 10:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('databank', '0010_auto_20180703_1937'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='property',
            options={'ordering': ['animal', 'parent']},
        ),
    ]
