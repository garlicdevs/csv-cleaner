from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
import tempfile
import shutil
from pathlib import Path
from django.conf import settings


class CsvTypeInferViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a temporary directory to store the uploaded file
        cls.temp_dir = tempfile.mkdtemp()
        # Path to the sample_data.csv within the temporary directory
        cls.file_path = Path(cls.temp_dir) / 'sample_data.csv'
        # Create a sample CSV file
        with open(cls.file_path, 'w') as f:
            f.write("""Name,Birthdate,Score,Grade
Alice,1990-01-01,90,A
Bob,1991-02-02,75,B
Charlie,1992-03-03,85,A
David,1993-04-04,70,B
Eve,1994-05-05,,A
""")

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory after the test run
        shutil.rmtree(cls.temp_dir)
        super().tearDownClass()

    def test_csv_type_infer_view(self):
        """Test the CSV type inference through the CsvTypeInferView."""
        url = reverse('cleaner-type-infer')

        # Prepare data and files to send in the POST request
        with open(self.file_path, 'rb') as file:
            data = {
                'document': file,
                'chunk_size': 1000000,
                'sample_size_per_chunk': 1000000,
                'random_state': 0,
                'valid_threshold': 0.5,
                'category_threshold': 0.5,
            }
            response = self.client.post(url, data, format='multipart', HTTP_X_API_KEY=settings.API_KEY,
                                        HTTP_ACCEPT='application/json')

        # Check if the response status is HTTP_202_ACCEPTED
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        self.assertIn('columns', response.json())
        for column in response.json()['columns']:
            self.assertIn(column['name'], ['Name', 'Birthdate', 'Score', 'Grade'])
            # Add more detailed assertions per column based on expected types
