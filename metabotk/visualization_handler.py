"""
Visualization module for MetaboTK
This module provides functions to visualize the results of principal component analysis (PCA) and plot metabolite
abundance data.
TODO: add more visualizations
"""

import seaborn as sns
import pandas as pd
from typing import Optional
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

    def plot_pca(self, pca=None, x="PC1", y="PC2", hue=None, style=None, savepath=None):
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
        style: str, optional
            Column name in sample metadata DataFrame to shape the points by.
        savepath: str, optional
            Path to save the plot as an image file. If not provided, the plot
            will not be saved.

        Returns
        -------
        plot: seaborn.axisgrid.FacetGrid
            Seaborn scatterplot object.
        """
        if not pca:
            print("PCA not found, computing now with 3 components...")
            pca = self.dimensionality_reduction.get_pca(n_components=3)
        plot = sns.scatterplot(data=pca, x=x, y=y, hue=hue, style=style)
        if savepath:
            plot.figure.savefig(savepath)
        return plot

    def plot_pca_grid(
        self,
        pca: pd.DataFrame = None,
        hue: Optional[str] = None,
        savepath: Optional[str] = None,
    ) -> sns.axisgrid.PairGrid:
        """
        Plot PCA results in a grid using seaborn's pairplot.

        Parameters
        ----------
        pca: pandas.DataFrame, optional
            DataFrame with PCA results. If not provided, it will be computed
            using the `get_pca` function from the `DimensionalityReduction` class.
        hue: str, optional
            Column name in sample metadata DataFrame to color the points by.
        savepath: str, optional
            Path to save the plot as an image file. If not provided, the plot
            will not be saved.

        Returns
        -------
        plot: seaborn.axisgrid.PairGrid
            Seaborn pairplot object.
        """
        if pca is None:
            print("PCA not found, computing now with 3 components...")
            pca = self.dimensionality_reduction.get_pca(n_components=3)
        plot = sns.pairplot(
            data=pca,
            vars=[col for col in pca.columns if col.startswith("PC")],
            hue=hue,
            diag_kind="kde",
            diag_kws={"linewidth": 0, "shade": False},
        )

        if savepath:
            plot.fig.savefig(savepath)

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
