# Generated by Django 3.2.6 on 2021-08-16 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0008_auto_20210816_0735'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='data',
            field=models.TextField(null=True, verbose_name='Необходимые данные для покупки'),
        ),
    ]