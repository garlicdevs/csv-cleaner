import pandas as pd
import numpy as np
import warnings
from collections import Counter
from typing import Any, Dict
from cleaner.utils import zip_float_dtype, zip_float_to_int_dtype, zip_int_dtype


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
    # Attempt conversion to datetime
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        converted = pd.to_datetime(valid_values, errors='coerce')

    proportion_valid = converted.notna().mean()

    if proportion_valid > threshold:
        return 'datetime64[ns]'
    else:
        return None


def check_timedelta(valid_values, threshold=0.5):
    """
    Check if a column can be converted to timedelta after removing NaN or empty values.

    Args:
    - column: The pandas Series to check.
    - threshold: The minimum proportion of valid timedelta values required.

    Returns:
    - 'timedelta64[ns]' if the column passes the timedelta check based on the threshold, None otherwise.
    """
    converted = pd.to_timedelta(valid_values, errors='coerce')
    if converted.notna().mean() > threshold:
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
    # Define all valid boolean representations
    valid_boolean_strs = {'true', 'false'}
    valid_boolean_types = {True, False}

    # Normalize string values and filter out valid boolean representations
    valid_values = column.map(lambda x: str(x).lower() if isinstance(x, str) else x)
    valid_values = valid_values[valid_values.apply(lambda x: x in valid_boolean_strs or x in valid_boolean_types)]

    if len(valid_values) == 0:
        return None

    # Check if the ratio of valid boolean values is above the threshold
    if len(valid_values) / len(column.dropna()) < threshold:
        return None

    # Check for two unique values forming a valid boolean pair
    boolean_pairs = [{'true', 'false'}, {True, False}]

    # Convert string representations to a uniform format for comparison
    uniform_boolean_values = set(valid_values.map(lambda x: True if x in ['true'] else False if x in ['false'] else x))

    # Check if unique values form one of the valid boolean pairs
    if len(uniform_boolean_values) == 2 and any(uniform_boolean_values == pair for pair in boolean_pairs):
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


def check_category(valid_values, unique_threshold=0.5):
    """
    Check if a column should be considered for categorization based on the proportion
    of unique non-NaN, non-empty values relative to the total number of non-NaN values,
    and ensuring that at least 50% of the categories have more than 2 elements.

    Args:
    - valid_values: The pandas Series to check.
    - unique_threshold: The maximum ratio of unique values to total non-NaN values
                        that justifies categorization. Defaults to 0.5.

    Returns:
    - 'category' if the column meets the criteria for categorization, None otherwise.
    """
    # Calculate the ratio of unique values to total valid values
    unique_ratio = len(valid_values.unique()) / len(valid_values)

    # Use Counter to get value frequencies
    value_counts = Counter(valid_values)

    # Calculate the number of categories with more than 2 elements
    categories_more_than_two = sum(1 for count in value_counts.values() if count > 2)

    # Check if at least 50% of the categories have more than 2 elements
    if unique_ratio <= unique_threshold and categories_more_than_two >= len(value_counts) / 2:
        return 'category'
    else:
        return None
