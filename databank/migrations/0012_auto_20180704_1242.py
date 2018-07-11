# Generated by Django 2.0.5 on 2018-07-04 10:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('databank', '0011_auto_20180704_1235'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='id',
        ),
        migrations.AddField(
            model_name='image',
            name='ID',
            field=models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular image across whole bank', primary_key=True, serialize=False),
        ),
    ]
