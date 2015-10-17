# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doslos', '0002_auto_20151017_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='level',
            name='description_de',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='level',
            name='description_en',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='level',
            name='name_de',
            field=models.CharField(null=True, max_length=255),
        ),
        migrations.AddField(
            model_name='level',
            name='name_en',
            field=models.CharField(null=True, max_length=255),
        ),
        migrations.AddField(
            model_name='word',
            name='value_de',
            field=models.CharField(null=True, max_length=1000),
        ),
        migrations.AddField(
            model_name='word',
            name='value_en',
            field=models.CharField(null=True, max_length=1000),
        ),
    ]
