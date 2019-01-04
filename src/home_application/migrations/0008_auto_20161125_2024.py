# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0007_filecell_content_new'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filecell',
            name='content',
            field=models.FileField(upload_to=b'uploads/', null=True, verbose_name='\u6587\u4ef6\u5185\u5bb9', blank=True),
        ),
    ]
