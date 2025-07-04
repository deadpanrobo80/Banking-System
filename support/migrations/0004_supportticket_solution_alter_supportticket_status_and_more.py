# Generated by Django 5.1.2 on 2024-10-15 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0003_rename_solution_supportticket_response_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportticket',
            name='solution',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='supportticket',
            name='status',
            field=models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('in_progress', 'In Progress')], default='open', max_length=20),
        ),
        migrations.AlterField(
            model_name='supportticket',
            name='subject',
            field=models.CharField(max_length=255),
        ),
    ]
