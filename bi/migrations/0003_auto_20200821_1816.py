# Generated by Django 3.0.8 on 2020-08-21 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bi', '0002_productsaledetail_create_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsaledetail',
            name='fee',
            field=models.FloatField(verbose_name='费用'),
        ),
    ]