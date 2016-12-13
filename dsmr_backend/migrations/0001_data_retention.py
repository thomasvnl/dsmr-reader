# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BackendSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('data_retention_in_weeks', models.IntegerField(blank=True, null=True, help_text='By default the application stores all readings taken. As there is a DSMR-reading every ten seconds, this results in over three million readings each year. This may or may not cause degraded performance in your setup used. For that reason you may want to apply retention to this data. Please note that enabling this feature will NOT discard ALL readings, as it will PRESERVE the first reading of each hour.', verbose_name='Data retention', choices=[(None, 'None (keep all readings)'), (1, 'Discard most readings after one week'), (4, 'Discard most readings after one month'), (26, 'Discard most readings after six months'), (52, 'Discard most readings after one year')], default=None)),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Backend configuration',
            },
        ),
    ]
