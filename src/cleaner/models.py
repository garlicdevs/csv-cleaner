from django.db import models
import json


class CsvFileInference(models.Model):
    file_name = models.CharField(max_length=255, unique=True, primary_key=True)
    columns_data = models.TextField(blank=True, null=True)  # Using TextField to store JSON data

    def set_columns_data(self, data):
        self.columns_data = json.dumps(data)

    def get_columns_data(self):
        return json.loads(self.columns_data) if self.columns_data else []
