# Generated by Django 3.2.6 on 2021-08-14 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_auto_20210814_1914'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Категории товаров',
                'verbose_name_plural': 'Категории товаров',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Название')),
                ('price1', models.PositiveIntegerField(verbose_name='Цена для некупившего пользователя')),
                ('price2', models.PositiveIntegerField(verbose_name='Цена для обычнаго пользователя')),
                ('price3', models.PositiveIntegerField(verbose_name='Цена для постоянного клиента')),
                ('price4', models.PositiveIntegerField(verbose_name='Цена для оптовика 1')),
                ('price5', models.PositiveIntegerField(verbose_name='Цена для оптовика 2')),
                ('text', models.TextField(verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Товары',
                'verbose_name_plural': 'Товары',
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='level',
            field=models.IntegerField(choices=[('1', 'Не купил'), ('2', 'Обычный клиент'), ('3', 'Постоянный клиент'), ('4', 'Оптовик 1'), ('5', 'Оптовик 2')], null=True, verbose_name='Уровень клиента'),
        ),
    ]