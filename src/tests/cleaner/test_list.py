from django.test import TestCase
from django.urls import reverse
from cleaner.models import CsvFileInference
import json
from django.conf import settings


class ListCsvFilesViewTest(TestCase):
    def setUp(self):
        CsvFileInference.objects.create(
            file_name='sample1.csv',
            columns_data=json.dumps([
                {"name": "Age", "inferred_type": "int64", "user_defined_type": "integer"},
                {"name": "Name", "inferred_type": "object", "user_defined_type": "text"}
            ])
        )
        CsvFileInference.objects.create(
            file_name='sample2.csv',
            columns_data=json.dumps([
                {"name": "Date", "inferred_type": "datetime64[ns]", "user_defined_type": "datetime"},
                {"name": "Score", "inferred_type": "float64", "user_defined_type": "float"}
            ])
        )

    def test_list_csv_files(self):
        # Get the URL for the 'list-csv-files' endpoint
        url = reverse('list-csv-files')
        # Make a GET request to the endpoint
        response = self.client.get(url, HTTP_X_API_KEY=settings.API_KEY, HTTP_ACCEPT='application/json')

        # Verify the response status code
        self.assertEqual(response.status_code, 200)

        # Deserialize the expected columns_data from JSON string to Python objects
        expected_response = [
            {
                "file_name": "sample1.csv",
                "columns_data": [
                    {"name": "Age", "inferred_type": "int64", "user_defined_type": "integer"},
                    {"name": "Name", "inferred_type": "object", "user_defined_type": "text"}
                ]
            },
            {
                "file_name": "sample2.csv",
                "columns_data": [
                    {"name": "Date", "inferred_type": "datetime64[ns]", "user_defined_type": "datetime"},
                    {"name": "Score", "inferred_type": "float64", "user_defined_type": "float"}
                ]
            }
        ]

        # Deserialize the actual response data to ensure matching formats for comparison
        actual_response = json.loads(response.content.decode('utf-8'))

        # Assert the contents without assuming order
        self.assertEqual(len(actual_response), len(expected_response))

        for item in expected_response:

            # Find the matching item by file_name in the actual response
            matching_item = next((ar for ar in actual_response if ar['fileName'] == item['file_name']), None)
            self.assertIsNotNone(matching_item)
