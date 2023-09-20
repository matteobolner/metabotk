from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np


#!!! HOW TO MAKE SKLEARN IDENTICAL TO R SCALE RESULTS
#https://stackoverflow.com/questions/27296387/difference-between-r-scale-and-sklearn-preprocessing-scale
"""
from sklearn.preprocessing import StandardScaler
import numpy as np

sc = StandardScaler()
sc.fit(data)
sc.scale_ = np.std(data, axis=0, ddof=1).to_list()
sc.transform(data)
"""



test=pd.read_table("/home/pelmo/work/workspace/relivestock_metabolomics/data/imputation/filtered_datasets/8/CS_T0/filtered_missing_only.tsv")


test=test[test.columns[6::]]


def getscaleval(x, dat):
    # Select the metabolite column x
    column_data = dat[x].values.reshape(-1, 1)

    # Scale the values and store mean and standard deviation
    scaler = StandardScaler()
    scaler.fit(data)
    scaler.scale_ = np.std(data, axis=0, ddof=1).to_list()
    # Create a DataFrame to store 'scale' and 'center' attributes
    scale_center_info = pd.DataFrame({
        'scale': scaler.scale_[0],
        'center': scaler.mean_[0]
    }, index=[x])

    return scale_center_info


getscaleval('X30', test)
scaler = StandardScaler(with_mean=True, with_std=True)


scaled_data = scaler.fit_transform(test[['X30']])
scaler.scale_
scaler.mean_

data=test['X30']

min_max_scaled_data = (data - data.min()) / (data.max() - data.min())
min_max_scaled_data
