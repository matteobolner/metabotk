import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class DimensionalityReduction:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def get_pca(self, n_components=3):
        """
        Perform Principal Component Analysis (PCA) on the data.

        Parameters:
            n_components (int, optional): Number of components for the PCA. Default is 3.

        Raises:
            ValueError: If the data contains NaN values or not all columns contain numeric data.

        Returns:
            pca: DataFrame containing the PCA-transformed data.
            pca_transformed: sklearn PCA object.
        """
        input_data = self.data_manager.data
        # Check if all columns have numeric data types
        if input_data.isnull().any().any():
            print("Data contains NaN values; columns with empty values were ignored")
            input_data = input_data.dropna(axis=1)
        if not input_data.select_dtypes(include=["number"]).equals(input_data):
            raise ValueError("Not all columns contain numeric data.")

        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(input_data)

        pca = PCA(n_components=n_components).fit(scaled_data)
        pca_transformed = pd.DataFrame(
            pca.transform(scaled_data),
            columns=[f"PC{i}" for i in range(1, n_components + 1)], index=self.data_manager.samples
        )
        pca_transformed = pd.concat([self.data_manager.sample_metadata, pca_transformed], axis=1)
        return pca_transformed, pca
