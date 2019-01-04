# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0008_auto_20161125_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filecell',
            name='content_new',
            field=models.BinaryField(default=b'', verbose_name='\u6587\u4ef6\u4e8c\u8fdb\u5236\u7c7b\u5bb9'),
        ),
    ]
