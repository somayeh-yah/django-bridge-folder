# Generated by Django 5.1.6 on 2025-05-30 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0020_alter_task_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
