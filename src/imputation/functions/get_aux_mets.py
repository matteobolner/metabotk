import pandas as pd
import numpy as np
#MICE STATSMODELS

def get_aux_mets(data_cor, Met, ccm, maxN=10):
    """
    Function that selects the 'maxN' strongest correlated metabolites.

    Parameters:
    - data_cor: DataFrame, the data correlation matrix for the metabolites.
    - Met: str, name of the metabolite column with missing values.
    - ccm: list, vector with the column names of the complete cases.
    - maxN: int, the maximum number of correlated metabolites to select.

    Returns:
    - Preds: list, a list of 'maxN' strongest correlated metabolites.
    """
    cor_x = data_cor.loc[Met]
    cor_x=cor_x[cor_x.index.isin(ccm)]
    cor_x_sorted = cor_x.sort_values(ascending=False)
    cor_x_sorted = cor_x_sorted.dropna()
    Preds = cor_x_sorted.head(maxN).index.tolist()
    return(Preds)

test=pd.read_table("/home/pelmo/work/workspace/relivestock_metabolomics/data/imputation/filtered_datasets/8/CS_T0/filtered_missing_only.tsv")


test=test[test.columns[6::]]
ccm=list(test.dropna(axis=1).columns)
data_cor=test.corr(method='pearson')

Met='X55'
maxN=10
cor_x = data_cor.loc[Met]
cor_x=cor_x[cor_x.index.isin(ccm)]
cor_x_sorted = cor_x.sort_values(ascending=False)
cor_x_sorted = cor_x_sorted.dropna()
Preds = cor_x_sorted.head(maxN).index.tolist()

cor_x_sorted

Preds
data_cor['X55']['X100003434']


X100003434

len(get_aux_mets(data_cor, 'X55', ccm, 10))


subset_df = DataFrame[ccm + icm_names]
data_cor = subset_df.corr()
