# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import doslos.models


class Migration(migrations.Migration):

    dependencies = [
        ('doslos', '0005_auto_20151017_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='probability',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='current_level',
            field=models.ForeignKey(default=doslos.models.get_default_level_id, to='doslos.Level'),
        ),
        migrations.AlterField(
            model_name='wordprogress',
            name='category',
            field=models.ForeignKey(default=doslos.models.get_default_category_id, to='doslos.Category'),
        ),
        migrations.AlterField(
            model_name='wordprogress',
            name='word',
            field=models.ForeignKey(related_name='progress', to='doslos.Word'),
        ),
        migrations.AlterUniqueTogether(
            name='wordprogress',
            unique_together=set([('user', 'word')]),
        ),
    ]
