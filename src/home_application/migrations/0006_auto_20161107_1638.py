# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0005_member_last_group_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='creator',
            field=models.ForeignKey(related_name='group_as_creator', verbose_name='\u521b\u5efa\u8005', blank=True, to='home_application.Member', null=True),
        ),
    ]
