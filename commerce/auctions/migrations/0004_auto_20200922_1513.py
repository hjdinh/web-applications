# Generated by Django 3.1 on 2020-09-22 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20200922_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=models.TextField(max_length=1000, null=True),
        ),
    ]
