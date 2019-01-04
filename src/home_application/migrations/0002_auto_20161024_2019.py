# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='username',
            field=models.CharField(default='', max_length=128, verbose_name='\u7528\u6237\u540d'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='member',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
