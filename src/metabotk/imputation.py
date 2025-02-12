import miceforest as mf
from metabotk.statistics_handler import get_top_n_correlations


def miceforest(
    data,
    n_correlated_metabolites,
    n_imputed_datasets=5,
    n_iterations=5,
    random_state=42,
    get_kernel=False,
):
    """
    Perform missing data imputation using MICE (Mixed-effects Imputation by Chained Equations).

    Parameters:
        data: Numeric pandas DataFrame containing the dataset to impute
        n_correlated_metabolites (int): Number of metabolites to use for correlated imputation.

    Returns:
        dict: Dictionary with imputed datasets, keys are integers starting from 1.
    """
    corrs = get_top_n_correlations(data_frame=data, n=n_correlated_metabolites)
    corrs_dict = {}
    for name, group in corrs.groupby(by="id_1"):
        corrs_dict[name] = group["id_2"].tolist()
    kds = mf.ImputationKernel(
        data=data,
        num_datasets=n_imputed_datasets,
        variable_schema=corrs_dict,
        save_all_iterations_data=True,
        random_state=random_state,
        # train_nonmissing=False,
        mean_match_strategy="shap",
    )
    kds.mice(
        iterations=n_iterations,
        verbose=True,
    )

    imputed = {
        dataset + 1: kds.complete_data(dataset=dataset)
        for dataset in range(n_imputed_datasets)
    }
    if get_kernel == True:
        return kds, imputed
    else:
        return imputed


class Imputation:
    """ """

    def __init__(self, dataset):
        """
        Initializes the class.
        """

        self.dataset = dataset

    def miceforest(
        self,
        n_correlated_metabolites=10,
        n_imputed_datasets=5,
        n_iterations=5,
        random_state=42,
        get_kernel=False,
    ):
        return miceforest(
            self.dataset.data.reset_index(drop=True),
            n_correlated_metabolites,
            n_imputed_datasets,
            n_iterations,
            random_state,
            get_kernel,
        )
