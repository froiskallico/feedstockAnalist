# Generated by Django 2.2.11 on 2020-04-17 18:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedStockAnalist', '0003_auto_20200417_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='created_by',
            field=models.ForeignKey(default='', on_delete='', to=settings.AUTH_USER_MODEL),
        ),
    ]
