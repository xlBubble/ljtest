# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300, verbose_name='\u5206\u7c7b\u540d\u79f0')),
                ('describe', models.CharField(default=b'', max_length=50, verbose_name='\u5206\u7c7b\u8bf4\u660e')),
                ('show_count', models.IntegerField(default=1, verbose_name='\u8ddf\u8fdb\u8bb0\u5f55\u9ed8\u8ba4\u663e\u793a\u6570\u91cf')),
                ('isActive', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6fc0\u6d3b')),
                ('ancient', models.ForeignKey(related_name='family', verbose_name='\u7956\u5148', blank=True, to='home_application.Category', null=True)),
                ('father', models.ForeignKey(related_name='son', verbose_name='\u7236\u7c7b', blank=True, to='home_application.Category', null=True)),
            ],
            options={
                'verbose_name': '\u5185\u5bb9\u5206\u7c7b',
                'verbose_name_plural': '\u5185\u5bb9\u5206\u7c7b',
            },
        ),
        migrations.CreateModel(
            name='FileCell',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u6587\u4ef6\u7684\u771f\u5b9e\u540d\u79f0')),
                ('name_ex', models.CharField(max_length=255, verbose_name='\u6587\u4ef6\u62d3\u5c55\u540d\uff0c\u65b9\u4fbf\u6392\u5e8f')),
                ('size', models.IntegerField(default=0, verbose_name='\u6587\u4ef6\u5927\u5c0f')),
                ('content', models.FileField(upload_to=b'uploads/', verbose_name='\u6587\u4ef6\u5185\u5bb9')),
                ('upload_time', models.DateTimeField(auto_now_add=True, verbose_name='\u4e0a\u4f20\u65f6\u95f4')),
                ('isActive', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6fc0\u6d3b')),
            ],
            options={
                'verbose_name': '\u6587\u4ef6\u7ba1\u7406',
                'verbose_name_plural': '\u6587\u4ef6\u7ba1\u7406',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=300, verbose_name='\u540d\u79f0')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u66f4\u65b0')),
                ('isActive', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6fc0\u6d3b')),
            ],
            options={
                'verbose_name': '\u4f1a\u8bae\u7ec4',
                'verbose_name_plural': '\u4f1a\u8bae\u7ec4',
            },
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host_order', models.TextField(default=b'', verbose_name='\u4e3b\u6301\u4eba\u987a\u5e8f')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u66f4\u65b0')),
                ('isActive', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6fc0\u6d3b')),
            ],
            options={
                'verbose_name': '\u4e3b\u6301\u4eba\u5217\u8868',
                'verbose_name_plural': '\u4e3b\u6301\u4eba\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=50, verbose_name='\u540d\u79f0')),
                ('content', models.TextField(default=b'', verbose_name='\u5185\u5bb9')),
                ('status', models.CharField(max_length=10, verbose_name='\u72b6\u6001', choices=[(b'Pending', '\u6302\u8d77'), (b'Processing', '\u8fdb\u884c\u4e2d'), (b'Finished', '\u5df2\u5b8c\u6210')])),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u66f4\u65b0')),
                ('finish_time', models.DateTimeField(null=True, verbose_name='\u5b8c\u6210\u65f6\u95f4', blank=True)),
                ('keep_top', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7f6e\u9876')),
                ('top_point', models.IntegerField(default=0, verbose_name='\u7f6e\u9876\u6307\u6570')),
                ('isActive', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6fc0\u6d3b')),
                ('category', models.ForeignKey(related_name='item', verbose_name='\u5206\u7c7b', to='home_application.Category')),
            ],
            options={
                'verbose_name': '\u5de5\u4f5c\u9879',
                'verbose_name_plural': '\u5de5\u4f5c\u9879',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=10, verbose_name='\u89d2\u8272', choices=[(b'Admin', '\u7ba1\u7406\u5458'), (b'Member', '\u666e\u901a\u6210\u5458'), (b'Stranger', '\u964c\u751f\u4eba')])),
                ('isActive', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6fc0\u6d3b')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u7528\u6237',
                'verbose_name_plural': '\u7528\u6237',
            },
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(verbose_name='\u5185\u5bb9')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u4e8e')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u66f4\u65b0')),
                ('isActive', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6fc0\u6d3b')),
                ('creator', models.ForeignKey(related_name='record_as_creator', verbose_name='\u521b\u5efa\u8005', to='home_application.Member')),
                ('item', models.ForeignKey(related_name='record', verbose_name='\u6240\u5c5e\u5de5\u4f5c\u9879', to='home_application.Item')),
                ('updater', models.ForeignKey(related_name='record_as_updater', verbose_name='\u6700\u540e\u4e00\u6b21\u7f16\u8f91\u8005', to='home_application.Member')),
            ],
            options={
                'verbose_name': '\u4e8b\u9879\u8ddf\u8fdb',
                'verbose_name_plural': '\u4e8b\u9879\u8ddf\u8fdb',
            },
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category_order', models.TextField(default=b'', verbose_name='\u7c7b\u522b\u987a\u5e8f(id)')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u540e\u66f4\u65b0')),
                ('isActive', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6fc0\u6d3b')),
                ('updater', models.ForeignKey(related_name='repository_as_updater', verbose_name='\u6700\u540e\u64cd\u4f5c\u8005', blank=True, to='home_application.Member')),
            ],
            options={
                'verbose_name': '\u4ed3\u5e93',
                'verbose_name_plural': '\u4ed3\u5e93',
            },
        ),
        migrations.AddField(
            model_name='item',
            name='creator',
            field=models.ForeignKey(related_name='item_as_creator', verbose_name='\u521b\u5efa\u8005', to='home_application.Member'),
        ),
        migrations.AddField(
            model_name='item',
            name='manager',
            field=models.ManyToManyField(related_name='item_as_manager', verbose_name='\u8d23\u4efb\u8005', to='home_application.Member'),
        ),
        migrations.AddField(
            model_name='item',
            name='member',
            field=models.ManyToManyField(related_name='item_as_member', verbose_name='\u8d1f\u8d23\u6210\u5458', to='home_application.Member', blank=True),
        ),
        migrations.AddField(
            model_name='item',
            name='updater',
            field=models.ForeignKey(related_name='item_as_updater', verbose_name='\u6700\u540e\u4e00\u6b21\u7f16\u8f91\u8005', to='home_application.Member'),
        ),
        migrations.AddField(
            model_name='host',
            name='updater',
            field=models.ForeignKey(related_name='host_as_updater', verbose_name='\u6700\u540e\u64cd\u4f5c\u8005', blank=True, to='home_application.Member'),
        ),
        migrations.AddField(
            model_name='group',
            name='focus',
            field=models.ManyToManyField(related_name='group_as_focus', verbose_name='\u5173\u6ce8\u4eba', to='home_application.Member', blank=True),
        ),
        migrations.AddField(
            model_name='group',
            name='host',
            field=models.ForeignKey(related_name='group', verbose_name='\u4e3b\u6301\u4eba\u5217\u8868', blank=True, to='home_application.Host', null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='manager',
            field=models.ManyToManyField(related_name='group_as_manager', verbose_name='\u7ba1\u7406\u5458', to='home_application.Member', blank=True),
        ),
        migrations.AddField(
            model_name='group',
            name='member',
            field=models.ManyToManyField(related_name='group_as_member', verbose_name='\u6210\u5458', to='home_application.Member', blank=True),
        ),
        migrations.AddField(
            model_name='group',
            name='repository',
            field=models.ForeignKey(related_name='group', verbose_name='\u4ed3\u5e93', blank=True, to='home_application.Repository', null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='updater',
            field=models.ForeignKey(related_name='group_as_updater', verbose_name='\u6700\u540e\u64cd\u4f5c\u8005', blank=True, to='home_application.Member'),
        ),
        migrations.AddField(
            model_name='filecell',
            name='group',
            field=models.ForeignKey(related_name='file', verbose_name='\u6240\u5c5e\u4f1a\u8bae\u7ec4', blank=True, to='home_application.Group', null=True),
        ),
        migrations.AddField(
            model_name='filecell',
            name='uploader',
            field=models.ForeignKey(related_name='file_cell_as_uploader', verbose_name='\u4e0a\u4f20\u8005', to='home_application.Member'),
        ),
        migrations.AddField(
            model_name='category',
            name='repository',
            field=models.ForeignKey(related_name='category', verbose_name='\u6240\u5c5e\u4ed3\u5e93', blank=True, to='home_application.Repository', null=True),
        ),
    ]
