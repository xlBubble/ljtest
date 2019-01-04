# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0003_member_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='describe',
            field=models.TextField(default=b'', verbose_name='\u5206\u7c7b\u8bf4\u660e'),
        ),
    ]
