# Generated by Django 3.1 on 2020-09-22 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listing_watchlist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='current_price',
            new_name='starting_bid',
        ),
    ]