import pyserrf as srf


class NormalizationHandler:
    """
    Class for performing normalization on metabolomics data.

    This class provides a simple interface to perform normalization on the data using various approaches.
    For now only SERRF is included.
    """

    def __init__(
        self,
        dataset_manager,
    ):
        """
        Initialize the class.
        """
        self._dataset_manager = dataset_manager

    def serrf(
        self,
        sample_type_column="measurement_group",
        batch_column="batch",
        time_column="time",
        other_columns=None,
        n_correlated_metabolites=10,
        random_state=None,
        threads=1,
    ):
        """
        Perform normalization using SERRF.
        Parameters
        ----------
        sample_type_column : str, optional
            The name of the column in the sample metadata with the sample type
            information (i.e qc or normal sample). The default value is
            'sampleType'.
        batch_column : str, optional
            The name of the column in the sample metadata with the batch
            information. If None, all samples are considered as part the same
            batch. The default value is 'batch'.
        time_column: str, optional
            The name of the column in the sample metadata with the injection time
            information.The default value is 'time'.
        other_columns : list of str or None, optional
            A list with the names of other metadata columns in the dataset; it is
            important to specify all the metadata columns to separate them from
            the metabolite abundance values. The default value is None
        random_state : int, RandomState instance, or None, optional
            The random seed used for all methods with a random component (i.e
            numpy normal distribution, sklearn random forest regressor). The
            default value is None, which means that a random seed is generated
            automatically. To obtain reproducible results, set a specific random
            seed.
        n_correlated_metabolites : int, optional
            The number of metabolites with the highest correlation to the
            metabolite to be normalized. The default value is 10.
        threads: int, optional
            Number of threads to use for parallel processing        Returns:
                dict: Dictionary with imputed datasets, keys are integers starting from 1.
        """
        serrf_instance = srf.SERRF(
            sample_type_column=sample_type_column,
            batch_column=batch_column,
            time_column=time_column,
            other_columns=other_columns,
            n_correlated_metabolites=n_correlated_metabolites,
            random_state=random_state,
            threads=threads,
        )
        input_dataset = self._dataset_manager.sample_metadata[
            [
                self._dataset_manager._sample_id_column,
                sample_type_column,
                batch_column,
                time_column,
            ]
        ].merge(self._dataset_manager.data, left_index=True, right_index=True)
        normalized = serrf_instance.fit_transform(input_dataset, return_data_only=True)
        return normalized
