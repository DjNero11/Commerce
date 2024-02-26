# Generated by Django 5.0 on 2024-01-02 17:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_listing_usr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='usr',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='usr', to=settings.AUTH_USER_MODEL),
        ),
    ]