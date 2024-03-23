from django.test import TestCase
from django.urls import reverse
import json
from django.conf import settings
from cleaner.models import CsvFileInference


class UpdateColumnDtypeViewTest(TestCase):
    def setUp(self):
        # Setup a CsvFileInference instance for testing
        self.test_file_name = 'test_file.csv'
        self.test_columns_data = json.dumps([
            {"name": "column1", "pandas_type": "float64", "friendly_name": "float"},
            {"name": "column2", "pandas_type": "object", "friendly_name": "text"}
        ])
        CsvFileInference.objects.create(file_name=self.test_file_name, columns_data=self.test_columns_data)

        # URL for the update-column-dtype endpoint
        self.update_url = reverse('update-column-dtype')

    def test_update_column_dtype(self):
        # Data to send in the request
        update_data = {
            "file_name": self.test_file_name,
            "columns": [
                {"name": "column1", "new_dtype": "integer"},
                {"name": "column2", "new_dtype": "category"}
            ]
        }

        response = self.client.post(self.update_url, data=json.dumps(update_data), content_type='application/json',
                                    HTTP_X_API_KEY=settings.API_KEY, HTTP_ACCEPT='application/json')

        self.assertEqual(response.status_code, 204)

        # Fetch the updated object from the database
        updated_obj = CsvFileInference.objects.get(file_name=self.test_file_name)

        # Convert the columns_data from JSON to Python list
        updated_columns_data = updated_obj.get_columns_data()

        # Assert the changes were made correctly
        self.assertEqual(updated_columns_data[0]["user_defined_type"], "integer")
        self.assertEqual(updated_columns_data[1]["user_defined_type"], "category")
