import pandas as pd
import numpy as np
import warnings
from collections import Counter
from typing import Any, Dict


def zip_int_dtype(series):
    min_val = series.min()
    max_val = series.max()

    if min_val >= np.iinfo(np.int8).min and max_val <= np.iinfo(np.int8).max:
        return 'Int8'
    elif min_val >= np.iinfo(np.int16).min and max_val <= np.iinfo(np.int16).max:
        return 'Int16'
    elif min_val >= np.iinfo(np.int32).min and max_val <= np.iinfo(np.int32).max:
        return 'Int32'
    else:
        return 'Int64'


def zip_float_to_int_dtype(series):
    # Attempt conversion to int64
    try:
        temp_series = series.astype('Int64')
    except TypeError:
        return str(series.dtype)

    # Convert back to float64
    temp_series_back_to_float64 = temp_series.astype('float64')

    # Check if the conversion back and forth results in the same data
    if np.allclose(series, temp_series_back_to_float64, rtol=1e-05, atol=1e-08, equal_nan=True):
        return zip_int_dtype(series)
    else:
        return str(series.dtype)


def zip_float_dtype(series):
    # Attempt conversion to float32
    temp_series = series.astype('float32')

    # Convert back to float64
    temp_series_back_to_float64 = temp_series.astype('float64')

    # Check if the conversion back and forth results in the same data
    if np.allclose(series, temp_series_back_to_float64, rtol=1e-05, atol=1e-08):
        return 'float32'
    else:
        return 'float64'
