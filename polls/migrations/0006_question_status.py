# Generated by Django 5.1 on 2024-09-15 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0005_alter_question_pub_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='status',
            field=models.CharField(default='active', max_length=20),
        ),
    ]