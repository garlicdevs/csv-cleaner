import pandas as pd
import numpy as np
import warnings
import os
from collections import Counter
from typing import Any, Dict
from cleaner.type_checker import check_boolean, check_numeric, check_complex, check_datetime, check_category, check_timedelta
from cleaner.utils import zip_float_dtype, zip_float_to_int_dtype, zip_int_dtype


class DataFrameTypeInferencer:
    """
    A class for inferring and converting data types of a pandas DataFrame.

    Attributes:
        file_path (str): The path to the CSV or Excel file.
        chunk_size (int): The size of chunks for processing large files. Default is 1,000,000.
        sample_size_per_chunk (int): Number of samples to take per chunk for type inference.
        random_state (int): Seed for the random number generator.
        valid_threshold (float): Threshold for considering a data type valid (default is 0.5).
        category_threshold (float): Threshold for considering categorization (default is 0.5).
    """

    def __init__(self, file_path: str, chunk_size: int = 1000000,
                 sample_size_per_chunk: int = 1000000, random_state: int = 0,
                 valid_threshold: float = 0.5, category_threshold: float = 0.5):
        """
        Initializes the DataFrameTypeInferencer with file path and processing parameters.
        """
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.sample_size_per_chunk = sample_size_per_chunk
        self.random_state = random_state
        self.valid_threshold = valid_threshold
        self.category_threshold = category_threshold

    def infer_dtype(self, column: pd.Series) -> str:
        """
        Infers the most appropriate data type for a given pandas Series (column).
        """
        # Filter out NaN or empty values
        valid_values = column.dropna().loc[column.astype(str).str.strip() != '']
        if len(valid_values) == 0:
            return 'object'

        if str(column.dtype) == 'object':
            for check in (check_boolean, check_numeric, check_complex, check_datetime, check_category):
                if check is check_category:
                    dtype = check(valid_values, unique_threshold=self.category_threshold)
                else:
                    dtype = check(valid_values, threshold=self.valid_threshold)
                if dtype is not None:
                    return dtype
        elif str(column.dtype).lower() in ['int8', 'int16', 'int32', 'int64']:
            dtype = zip_int_dtype(column)
            return dtype
        elif str(column.dtype) in ['float32', 'float64']:
            dtype = zip_float_to_int_dtype(column)
            if dtype in ['float32', 'float64']:
                dtype = zip_float_dtype(column)
            return dtype
        return 'object'

    def sample_and_infer_types(self) -> Dict[str, str]:
        """
        Samples the DataFrame and infers data types for each column.
        """
        sampled_df = pd.DataFrame()

        if self.file_path.endswith('.csv'):
            try:
                reader = pd.read_csv(self.file_path, chunksize=self.chunk_size, low_memory=True)
            except UnicodeDecodeError:
                reader = pd.read_csv(self.file_path, chunksize=self.chunk_size, low_memory=True, encoding='unicode_escape')

            for chunk in reader:
                if len(chunk) < self.sample_size_per_chunk:
                    sampled_chunk = chunk  # Take the whole chunk if it's smaller than the sample size
                else:
                    sampled_chunk = chunk.sample(n=self.sample_size_per_chunk, random_state=self.random_state)
                sampled_chunk = sampled_chunk.loc[:, ~sampled_chunk.columns.str.contains('^Unnamed')]
                sampled_df = pd.concat([sampled_df, sampled_chunk], ignore_index=True)

        elif self.file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
            if len(df) < self.sample_size_per_chunk:
                sampled_df = df
            else:
                sampled_df = df.sample(n=self.sample_size_per_chunk, random_state=self.random_state)
            sampled_df = sampled_df.loc[:, ~sampled_df.columns.str.contains('^Unnamed')]
        else:
            raise ValueError("Unsupported file format.")

        type_map = {col: self.infer_dtype(sampled_df[col]) for col in sampled_df.columns}

        return type_map

    def convert_df_dtypes(self, type_map: Dict[str, str]) -> pd.DataFrame:
        """
        Converts the DataFrame columns to the inferred data types.
        """
        try:
            df = pd.read_csv(self.file_path, low_memory=True)
        except UnicodeDecodeError:
            df = pd.read_csv(self.file_path, low_memory=True, encoding='unicode_escape')

        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        print('###### BEFORE CONVERSION')
        print(df.dtypes)
        print('\n\n')

        for column, dtype in type_map.items():
            # noinspection PyBroadException
            try:
                if dtype == 'datetime64[ns]':
                    df[column] = pd.to_datetime(df[column], errors='coerce', format='mixed')
                elif dtype == 'category':
                    df[column] = df[column].astype('category')
                elif dtype in ['Int8', 'Int16', 'Int32', 'Int64']:
                    df[column] = pd.to_numeric(df[column], errors='coerce').astype(dtype)
                elif dtype in ['float32', 'float64']:
                    df[column] = pd.to_numeric(df[column], errors='coerce').astype(dtype)
                elif dtype == 'bool':
                    df[column] = df[column].astype('bool')
                elif dtype == 'complex128':
                    df[column] = df[column].apply(complex)
                else:
                    df[column] = df[column].astype(dtype)
            except:
                # Rollback to original type
                continue

        print('###### AFTER CONVERSION')
        print(df.dtypes)
        return df

    def infer_and_convert(self):
        """
        Main method to perform both inference and conversion for the DataFrame.
        """
        type_map = self.sample_and_infer_types()
        return self.convert_df_dtypes(type_map)


if __name__ == '__main__':
    files = os.listdir('../csv/')
    for file in files:
        file_path = os.path.join('../csv', file)
        inference = DataFrameTypeInferencer(file_path)
        inference.infer_and_convert()
