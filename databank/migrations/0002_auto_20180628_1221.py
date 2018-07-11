# Generated by Django 2.0.5 on 2018-06-28 10:21

import databank.models
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('databank', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('ENAR', models.CharField(help_text='ENAR ID', max_length=10, verbose_name='ENAR ID')),
                ('date', models.DateField(help_text='Birth Date')),
                ('image', models.ImageField(upload_to=databank.models.upl_file_name, verbose_name='Image')),
                ('meas', models.FileField(upload_to=databank.models.upl_file_name, verbose_name='Measurements')),
                ('ID', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular Individual across whole bank', primary_key=True, serialize=False)),
                ('father', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_f', to='databank.Individual')),
                ('location', models.ForeignKey(help_text='Birth Location', null=True, on_delete=django.db.models.deletion.SET_NULL, to='databank.Location')),
                ('mother', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_m', to='databank.Individual')),
                ('species', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='databank.Species')),
            ],
            options={
                'ordering': ['ID', 'ENAR', 'date', 'subspecies', 'location'],
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('name', models.CharField(help_text='Enter the option name', max_length=200)),
                ('ID', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular option across whole bank', primary_key=True, serialize=False)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('ID', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular base property across whole bank', primary_key=True, serialize=False)),
                ('numVal', models.FloatField(help_text='Enter the value of the numerical option')),
                ('textVal', models.CharField(help_text='Enter the minimal value of the text option', max_length=200)),
                ('animal', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='databank.Individual')),
            ],
            options={
                'ordering': ['parent'],
            },
        ),
        migrations.CreateModel(
            name='Property_base',
            fields=[
                ('name', models.CharField(help_text='Enter the property name', max_length=200)),
                ('ID', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular base property across whole bank', primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('N', 'Node'), ('T', 'Text'), ('N', 'Number'), ('C', 'Choice')], max_length=1)),
                ('maxVal', models.FloatField(default=1.0, help_text='Enter the maximal value of the numerical option')),
                ('minVal', models.FloatField(default=0.0, help_text='Enter the minimal value of the numerical option')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='databank.Property_base')),
                ('species', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='databank.Species')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Subspecies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter the subspecies name', max_length=200)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='phenome',
            name='location',
        ),
        migrations.RemoveField(
            model_name='phenome',
            name='species',
        ),
        migrations.DeleteModel(
            name='Phenome',
        ),
        migrations.AddField(
            model_name='property',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='databank.Property_base'),
        ),
        migrations.AddField(
            model_name='option',
            name='property',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='databank.Property_base'),
        ),
        migrations.AddField(
            model_name='individual',
            name='subspecies',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='databank.Subspecies'),
        ),
    ]