# Generated by Django 5.1.6 on 2025-05-12 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0013_alter_task_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.CharField(blank=True, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], max_length=20),
        ),
    ]
