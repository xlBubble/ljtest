# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0002_auto_20161024_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='theme',
            field=models.CharField(default=b'theme1', max_length=100, verbose_name='\u4e3b\u9898'),
        ),
    ]
