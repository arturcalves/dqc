# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-26 23:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dqc', '0004_auto_20160326_1504'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datacolumnconstraint',
            old_name='arguments',
            new_name='argument',
        ),
        migrations.RemoveField(
            model_name='datacolumnconstraint',
            name='validation_schema',
        ),
    ]
