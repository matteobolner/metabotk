from typing import List
import pandas as pd
import pyserrf as srf
from skloess import LOESS


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
        dataset,
        sample_type_column="measurement_group",
        batch_column="batch",
        time_column="time",
        other_columns=None,
        n_correlated_metabolites=10,
        random_state=None,
        threads=1,
        cross_validation=False,
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
        normalized = serrf_instance.fit_transform(dataset, return_data_only=True)
        return normalized

    def serrf_CV(
        self,
        dataset,
        n_splits=5,
        sample_type_column="measurement_group",
        batch_column="batch",
        time_column="time",
        other_columns=None,
        n_correlated_metabolites=10,
        random_state=None,
        threads=1,
    ):
        """
        Perform cross-validation using SERRF.

        Parameters
        ----------
        dataset : DataFrame
            The dataset to perform cross-validation on.
        n_splits : int, optional
            The number of splits to perform (default: 5).
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
        n_correlated_metabolites : int, optional
            The number of metabolites with the highest correlation to the
            metabolite to be normalized. The default value is 10.
        random_state : int, RandomState instance, or None, optional
            The random seed used for all methods with a random component (i.e
            numpy normal distribution, sklearn random forest regressor). The
            default value is None, which means that a random seed is generated
            automatically. To obtain reproducible results, set a specific random
            seed.
        threads: int, optional
            Number of threads to use for parallel processing.

        Returns
        -------
        dict
            Dictionary with cross-validated datasets, keys are integers starting from 1.
        """
        # Perform cross-validation
        raw_variations, normalized_variations = srf.cross_validate(
            dataset,
            n_splits=n_splits,
            sample_type_column=sample_type_column,
            batch_column=batch_column,
            time_column=time_column,
            other_columns=other_columns,
            n_correlated_metabolites=n_correlated_metabolites,
            random_state=random_state,
            threads=threads,
        )
        return raw_variations, normalized_variations

    def loess_single_metabolite(
        self,
        metabolite: str,
        degree: int,
        smoothing: float,
        rescale: bool,
        qc_samples: List[str],
        injection_order_col: str,
    ) -> pd.Series:
        """
        Perform LOESS normalization on a single metabolite.

        Parameters
        ----------
        metabolite : str
            The name of the metabolite to normalize.
        degree : int
            The degree of the LOESS polynomial.
        smoothing : float
            The smoothing parameter for LOESS.
        rescale : bool
            Whether to rescale the normalized values to the median.
        qc_samples : List[str]
            The names of the QC samples.
        injection_order_col : str
            The name of the column containing the injection order.

        Returns
        -------
        pd.Series
            The normalized values for the metabolite.
        """
        # Extract the metabolite and remove missing values
        data = self._dataset_manager.extract_metabolites(metabolite)

        # Extract the QC samples
        qc = data.loc[qc_samples]
        x_qc = qc[injection_order_col]
        y_qc = qc[metabolite]

        # Perform LOESS normalization
        loess = LOESS(degree=degree, smoothing=smoothing)
        loess.fit(x_qc.values, y_qc.values)
        pred = loess.predict(data[injection_order_col].values)
        norm = data[metabolite] - pred

        # Rescale the normalized values if requested
        if rescale:
            median = data[metabolite].median()
            norm = norm + median

        return norm

    def loess(
        self,
        degree: int,
        smoothing: float,
        rescale: bool,
        qc_samples: List[str],
        injection_order_col: str,
        inplace: bool = True,
    ):
        """
        Perform LOESS normalization on all metabolites in the dataset.

        Parameters
        ----------
        degree : int
            The degree of the LOESS polynomial.
        smoothing : float
            The smoothing parameter for LOESS.
        rescale : bool
            Whether to rescale the normalized values to the median.
        qc_samples : List[str]
            The names of the QC samples.
        injection_order_col : str
            The name of the column containing the injection order.
        inplace : bool, optional
            Whether to perform the normalization inplace. Default is True.

        Returns
        -------
        pd.DataFrame
            The normalized data.
        """
        # Loop over all metabolites in the dataset
        data = self._dataset_manager.data
        for metabolite in self._dataset_manager.metabolites:
            normalized_metabolite = self.loess_single_metabolite(
                metabolite,
                degree,
                smoothing,
                rescale,
                qc_samples,
                injection_order_col,
            )
            data[metabolite] = normalized_metabolite
        if inplace:
            self._dataset_manager.data = data
        else:
            return data
