# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0004_auto_20161026_1637'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='last_group_id',
            field=models.IntegerField(default=0, verbose_name='\u6700\u8fd1\u8fdb\u5165\u7684\u5c0f\u7ec4'),
        ),
    ]
