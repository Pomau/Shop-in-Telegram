# Generated by Django 3.2.6 on 2021-08-14 20:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_alter_profile_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='сat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.category'),
        ),
    ]
