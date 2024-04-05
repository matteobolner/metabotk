import numpy as np

def detect_outliers(data, threshold):
    '''
    Get outlier values in a list/array using the Interquartile Range (IQR) method.
    See https://github.com/MRCIEU/metaboprep for details on the method and threshold: "outliers determined as those +/- 5 IQR of the median."

    Parameters:
    - values: list, array, or Series containing numerical data
    - threshold: multiplier for IQR to determine outliers

    Returns:
    - Boolean array indicating outliers (True) and non-outliers (False)
    '''
    median=np.nanmedian(data)
    q1 = np.nanquantile(data, 0.25)
    q3 = np.nanquantile(data, 0.75)
    iqr = q3 - q1
    cutoff_lower = median-(threshold*iqr)
    cutoff_upper = median+(threshold*iqr)
    is_outlier = (data < cutoff_lower) | (data > cutoff_upper)
    return(is_outlier)

def outliers_matrix(data_frame, threshold=5):
    '''
    Get a matrix of value outliers over the whole dataset columns
    '''
    matrix=data_frame.apply(lambda x: detect_outliers(x, threshold=threshold))
    return matrix
