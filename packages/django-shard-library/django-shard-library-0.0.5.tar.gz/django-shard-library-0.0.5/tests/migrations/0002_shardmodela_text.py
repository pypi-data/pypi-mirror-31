# Generated by Django 2.0.2 on 2018-04-12 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shardmodela',
            name='text',
            field=models.CharField(blank=True, max_length=64, verbose_name='더미 텍스트'),
        ),
    ]
