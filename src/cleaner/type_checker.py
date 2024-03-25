import pandas as pd
import numpy as np
import warnings
from collections import Counter
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from typing import Any, Dict
from cleaner.utils import zip_float_dtype, zip_float_to_int_dtype, zip_int_dtype
from sklearn.metrics import silhouette_score
from dateutil import parser
from pytimeparse.timeparse import timeparse


# Attempt conversion to datetime
def try_parse_date(x):
    # noinspection PyBroadException
    try:
        # Attempt to parse the date
        parsed_dt = parser.parse(str(x))
        return pd.to_datetime(parsed_dt, errors='coerce', exact=False)
    except:
        # Return pd.NaT in case of any parsing errors
        return pd.NaT


def check_datetime(valid_values, threshold=0.5):
    """
    Check if a column can be converted to datetime after removing NaN or empty values.

    Args:
    - column: The pandas Series to check.
    - threshold: The minimum proportion of valid datetime values required to consider
                 the column as datetime type.

    Returns:
    - The string 'datetime64[ns]' if the column passes the datetime check based on the threshold,
      None otherwise.
    """
    converted = valid_values.apply(lambda x: try_parse_date(x) if pd.notnull(x) else pd.NaT)

    # Calculate the proportion of valid datetime values
    proportion_valid = converted.notna().mean()

    if proportion_valid > threshold:
        return 'datetime64[ns]'
    else:
        return None


def try_parse_timedelta(x):
    # noinspection PyBroadException
    try:
        # Attempt to parse the duration string, timeparse returns the duration in seconds
        duration_in_seconds = timeparse(str(x))
        if duration_in_seconds is not None:
            # Convert the duration from seconds to a pandas Timedelta object
            return pd.to_timedelta(duration_in_seconds, unit='s')
        else:
            # If timeparse returns None, it means parsing was unsuccessful
            return pd.NaT
    except:
        return pd.NaT


def check_timedelta(valid_values, threshold=0.5):
    """
    Check if a pandas Series can be converted to timedelta after removing NaN or empty values,
    using custom parsing logic for a variety of string formats, with robust error handling.

    Args:
    - valid_values: The pandas Series to check.
    - threshold: The minimum proportion of valid timedelta values required.

    Returns:
    - 'timedelta64[ns]' if the series passes the timedelta check based on the threshold, None otherwise.
    """
    converted = valid_values.apply(lambda x: try_parse_timedelta(x) if pd.notnull(x) else pd.NaT)
    converted_timedeltas = pd.Series(converted).apply(lambda x: pd.to_timedelta(x, errors='coerce'))

    if converted_timedeltas.notna().mean() > threshold:
        return 'timedelta64[ns]'
    return None


def check_boolean(column, threshold=0.5):
    """
    Check if a column can be converted to boolean after removing NaN or empty values.
    First, filter for valid boolean strings or boolean types. If the ratio of valid
    boolean values exceeds the threshold, then check if these values form one of the
    valid two unique value pairs representing boolean logic.

    Args:
    - column: The pandas Series to check.
    - threshold: The minimum proportion of valid boolean values required.

    Returns:
    - 'bool' if the valid boolean values exceed the threshold and form two unique pairs,
      None otherwise.
    """
    # Update valid boolean representations to include additional True values
    valid_true_strs = {'1', 't', 'true', 'yes'}
    valid_false_strs = {'0', 'f', 'false', 'no'}
    valid_boolean_types = {True, False, 1, 0}

    # Normalize string values and filter out valid boolean representations
    valid_values = column.map(lambda x: str(x).lower() if isinstance(x, str) else x)
    valid_values = valid_values[valid_values.apply(lambda x: x in valid_true_strs or x in valid_false_strs or x in valid_boolean_types)]

    if len(valid_values) == 0:
        return None

    # Check if the ratio of valid boolean values is above the threshold
    if len(valid_values) / len(column.dropna()) < threshold:
        return None

    # Convert all valid representations to True or False for uniform comparison
    uniform_boolean_values = set(valid_values.map(lambda x: True if x in valid_true_strs else False if x in valid_false_strs or x == 0 else x))

    # Check if unique values form a valid boolean set
    if len(uniform_boolean_values) == 2:
        return 'bool'
    else:
        return None


def check_complex(valid_values, threshold=0.5):
    """
    Check if a column can be converted to complex numbers after removing NaN or empty values.
    If more than a specified threshold of the column can be converted without error,
    it is classified as 'complex128'.

    Args:
    - column: The pandas Series to check.
    - threshold: The minimum proportion of values required to identify the column as complex.
                 Defaults to 0.5.

    Returns:
    - 'complex128' if the column predominantly contains complex numbers, None otherwise.
    """
    # Attempt to convert valid values to complex numbers, coercing errors to NaN
    try:
        complex_series = valid_values.apply(lambda x: complex(x))
        # Check if the conversion succeeded without producing NaNs
        proportion_valid = complex_series.apply(lambda x: not pd.isna(x)).mean()

        if proportion_valid > threshold:
            return 'complex128'
    except ValueError:
        return None

    return None


def check_numeric(valid_values, threshold=0.5):
    """
    Check if a column can be converted to numeric types after removing NaN or empty values.
    Determines the most suitable numeric type (int or float) and size based on valid values.

    Args:
    - column: The pandas Series to check.
    - threshold: The minimum proportion of values required to identify the column as numeric.

    Returns:
    - The string representing the most suitable numeric type and size, or None if the column
      cannot be predominantly converted to numeric.
    """
    # Convert to numeric, coercing errors
    numeric_series = pd.to_numeric(valid_values, errors='coerce')

    # Ensure there's a significant proportion of numeric values
    if numeric_series.notna().mean() < threshold:
        return None

    # Now considering only valid numeric values for type determination
    numeric_series = numeric_series.dropna()

    if numeric_series.apply(float.is_integer).all():
        # Determine the smallest suitable integer type
        if numeric_series.between(np.iinfo(np.int8).min, np.iinfo(np.int8).max).all():
            return 'Int8'
        elif numeric_series.between(np.iinfo(np.int16).min, np.iinfo(np.int16).max).all():
            return 'Int16'
        elif numeric_series.between(np.iinfo(np.int32).min, np.iinfo(np.int32).max).all():
            return 'Int32'
        return 'Int64'
    else:
        return zip_float_dtype(numeric_series)


def check_category(valid_values):
    """
    Determine if a pandas Series is more efficiently stored as 'category' or 'text',
    using memory efficiency and a basic feature-based clustering analysis.

    Args:
    - valid_values: The pandas Series to check.

    Returns:
    - 'category' if the data is both memory efficient as category and shows tight clustering based on basic features,
      'text' if it is more memory efficient but does not show tight clustering,
      or 'ineligible' if not more memory efficient as category.
    """
    # Initial memory usage comparison
    memory_usage_text = valid_values.memory_usage(deep=True)
    memory_usage_category = valid_values.astype('category').memory_usage(deep=True)

    if memory_usage_category < memory_usage_text:
        valid_texts = valid_values.dropna().astype(str)

        if len(set(valid_texts)) <= 1:  # All values are identical or only one value exists
            return 'category'

        # Feature extraction: Use string length
        features = np.array(valid_texts.str.len()).reshape(-1, 1)
        features = StandardScaler().fit_transform(features)  # Standardize features

        # Apply DBSCAN
        dbscan = DBSCAN(eps=0.5, min_samples=5).fit(features)
        labels = dbscan.labels_

        # Number of clusters in labels, ignoring noise if present
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

        print('Number of clusters:', n_clusters_)

        if n_clusters_ > 1:
            return None
        else:
            return 'category'
    else:
        return None
