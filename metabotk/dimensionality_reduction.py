import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import sys


class DimensionalityReduction:
    """
    Class for performing dimensionality reduction on metabolomics data.

    This class provides a simple interface to perform Principal Component
    Analysis (PCA) on the data.
    """

    def __init__(self, data_manager):
        """
        Initialize the class.

        Parameters:
            data_manager (DataManager): DataManager instance containing the data.
        """
        self.data_manager = data_manager

    def get_pca(self, n_components=3, get_pca_object=False):
        """
        Perform Principal Component Analysis (PCA) on the data.

        Parameters:
            n_components (int, optional): Number of components for the PCA. Default is 3.

        Raises:
            ValueError: If the data contains NaN values or not all columns contain numeric data.

        Returns:
            pca_transformed (DataFrame): DataFrame containing the PCA-transformed data.
            pca (PCA): sklearn PCA object.
        """
        input_data = self.data_manager.data
        # Check if all columns have numeric data types
        if input_data.isnull().any().any():
            # Ignore columns with empty values
            print(
                "Data contains NaN values; columns with empty values were ignored",
                file=sys.stderr,
            )
            input_data = input_data.dropna(axis=1)
        if not input_data.select_dtypes(include=["number"]).equals(input_data):
            raise ValueError("Not all columns contain numeric data.")

        # Normalize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(input_data)

        # Perform PCA
        pca = PCA(n_components=n_components).fit(scaled_data)

        # Transform data
        pca_transformed = pd.DataFrame(
            pca.transform(scaled_data),
            columns=[f"PC{i}" for i in range(1, n_components + 1)],
            index=self.data_manager.data.index,
        )

        # Concatenate with sample metadata
        pca_transformed = self.data_manager.sample_metadata.merge(
            pca_transformed, left_index=True, right_index=True
        )
        if get_pca_object == True:
            return pca_transformed, pca
        else:
            return pca_transformed
