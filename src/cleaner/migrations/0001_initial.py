# Generated by Django 5.0.3 on 2024-03-22 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CsvFileInference",
            fields=[
                (
                    "file_name",
                    models.CharField(
                        max_length=255, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("columns_data", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
