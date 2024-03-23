from django.test import TestCase
from pathlib import Path
import pandas as pd
from cleaner.inferencer import DataFrameTypeInferencer


class DataFrameTypeInferencerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.file_path = Path(__file__).resolve().parent / 'sample_data.csv'

    def test_infer_and_convert(self):
        """Test the infer and convert process of the DataFrameTypeInferencer."""
        inference = DataFrameTypeInferencer(str(self.file_path))
        df = inference.infer_and_convert()

        # Check if 'Name' column is of type object
        self.assertTrue(pd.api.types.is_object_dtype(df['Name']), "Name column is not of type object")

        # Check if 'Birthdate' column is of type datetime64[ns]
        self.assertTrue(pd.api.types.is_datetime64_ns_dtype(df['Birthdate']),
                        "Birthdate column is not of type datetime64[ns]")

        # Check if 'Score' column is of type Int8
        self.assertTrue(pd.api.types.is_integer_dtype(df['Score']) and df['Score'].dtype.name == "Int8",
                        "Score column is not of type Int8")

        # Check if 'Grade' column is of type category
        self.assertTrue(isinstance(df['Grade'].dtype, pd.CategoricalDtype), "Grade column is not of type category")
