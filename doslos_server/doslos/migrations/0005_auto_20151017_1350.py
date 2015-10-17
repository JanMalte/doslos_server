# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doslos', '0004_auto_20151017_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='next_category_threshold',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
