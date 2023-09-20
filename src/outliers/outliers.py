import numpy as np

def get_outliers(input_array, quartile_size=0.25):
    l = np.array(input_array)
    top_quartile=np.quantile(l, 1-quartile_size)
    bottom_quartile=np.quantile(l, quartile_size)
    top_outliers=l[l > top_quartile]
    bottom_outliers=l[l < bottom_quartile]
    return(np.concatenate((bottom_outliers,top_outliers), axis=0))
