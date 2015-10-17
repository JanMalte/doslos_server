# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doslos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='current_level',
            field=models.ForeignKey(blank=True, null=True, to='doslos.Level'),
        ),
    ]
