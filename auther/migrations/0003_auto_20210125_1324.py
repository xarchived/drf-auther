# Generated by Django 3.1.5 on 2021-01-25 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auther', '0002_auto_20210116_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.TextField(null=True),
        ),
    ]