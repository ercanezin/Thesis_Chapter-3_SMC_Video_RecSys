# Generated by Django 2.1.2 on 2018-10-30 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0016_auto_20181029_1654'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bundle',
            old_name='bundle_name',
            new_name='name',
        ),
    ]
