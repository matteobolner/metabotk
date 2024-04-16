import seaborn as sns
from metabotk.dimensionality_reduction import DimensionalityReduction


class Visualization:
    def __init__(self, data_manager) -> None:
        """
        Initialize the class.

        Parameters:
        ----------
        data_manager: Object
            Instance of DataManager class
        """
        self.data_manager = data_manager
        """Instance of DataManager class"""

        self.dimensionality_reduction = DimensionalityReduction(
            data_manager=self.data_manager
        )
        """Instance of DimensionalityReduction class"""

    def plot_pca(self, pca=None, x="PC1", y="PC2", hue=None, savepath=None):
        """
        Plot the results of principal component analysis (PCA).

        This function plots the PCA results using seaborn's scatterplot function.
        If no PCA data is provided, it will compute the PCA with 3 components
        and plot the results.

        Parameters
        ----------
        pca: pandas.DataFrame, optional
            DataFrame with PCA results. If not provided, it will be computed
            using the `get_pca` function from the `DimensionalityReduction` class.
        x: str, default='PC1'
            Name of the X-axis.
        y: str, default='PC2'
            Name of the Y-axis.
        hue: str, optional
            Column name in sample metadata DataFrame to color the points by.
        savepath: str, optional
            Path to save the plot as an image file. If not provided, the plot
            will not be saved.

        Returns
        -------
        plot: seaborn.axisgrid.FacetGrid
            Seaborn scatterplot object.
        """
        if pca:
            plot = sns.scatterplot(data=pca, x=x, y=y, hue=hue)
        else:
            print("PCA not found, computing now with 3 components...")
            pca = self.dimensionality_reduction.get_pca(n_components=3)
            plot = sns.scatterplot(data=pca, x=x, y=y, hue=hue)
        if savepath:
            plot.figure.savefig(savepath)
        return plot

    def plot_metabolite(self, metabolite, x=None, hue=None, savepath=None):
        """
        Plot metabolite abundance data.

        Parameters
        ----------
        metabolite : str
            Name of the metabolite.
        x : str, optional
            Name of the X-axis. Default is the class sample ID column.
        hue : str, optional
            Column name in sample metadata DataFrame to color the points by.
            Default is None.
        savepath : str, optional
            Path to save the plot as an image file. Default is None.

        Returns
        -------
        plot : seaborn.axisgrid.FacetGrid
            Seaborn scatterplot object.
        """
        if not x:
            x = self.data_manager._sample_id_column
        data = self.data_manager.extract_metabolites(metabolite)
        plot = sns.scatterplot(data=data, x=x, y=str(metabolite), hue=hue)
        if savepath:
            plot.figure.savefig(savepath)
        return plot
