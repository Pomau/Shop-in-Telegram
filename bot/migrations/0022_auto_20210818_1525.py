# Generated by Django 3.2.6 on 2021-08-18 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0021_auto_20210818_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='ask',
            field=models.TextField(blank=True, null=True, verbose_name="Вопросы к товару (разделение на отдельные сообщения ';')"),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name="Подробное описание (разделение на отдельные сообщения ';')"),
        ),
    ]