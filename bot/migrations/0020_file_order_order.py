# Generated by Django 3.2.6 on 2021-08-18 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0019_auto_20210818_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='file_order',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.order'),
        ),
    ]
