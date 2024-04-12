"""
This module provides feature selection methods using scikit-learn.

Currently implemented methods:

* Boruta feature selection using the BorutaPy algorithm from boruta

"""

from sklearn.ensemble import RandomForestClassifier
from boruta import BorutaPy
import pandas as pd


class FeatureSelection:
    """
    Class for feature selection

    Attributes:
        data_manager (DatasetManager): DatasetManager object with data to be selected
        threads (int): Number of threads to use for parallel processing
        random_state (int): Random state for reproducibility
        group (str): Column name containing sample class information
    """

    def __init__(self, data_manager, threads=1, random_state=42, group="GROUP"):
        """
        Initiate the class

        Args:
            data_manager (DatasetManager): DatasetManager object with data to be selected
            threads (int): Number of threads to use for parallel processing
            random_state (int): Random state for reproducibility
            group (str): Column name containing sample class information
        """
        self.data_manager = data_manager
        self.threads = threads
        self.random_state = random_state
        self.group = group

    def setup_random_forest(
        self, random_state=42, max_depth=None, class_weight=None, **kwargs
    ):
        """
        Setup random forest

        Args:
            random_state (int): Random state for reproducibility
            max_depth (int): Max depth of the tree
            class_weight (dict): Dictionary with class weights

        Returns:
            RandomForestClassifier: Random Forest classifier
        """
        rf = RandomForestClassifier(
            n_jobs=self.threads,
            class_weight=class_weight,
            max_depth=max_depth,
            random_state=random_state,
        )
        return rf

    def boruta(
        self,
        max_depth=None,
        class_weight="balanced",
        n_estimators="auto",
        alpha=0.01,
        max_iterations=1000,
        random_state=42,
        get_model=False,
    ):
        """
        Boruta feature selection

        Performs Boruta feature selection using the BorutaPy algorithm.

        Args:
            max_depth (int): Max depth of the trees. If None, then no
                limit is set.
            class_weight (dict): Dictionary with class weights.
            n_estimators (int): Number of estimators for the Random Forest.
                If "auto", then the best value will be chosen.
            alpha (float): Confidence level for selecting features.
            max_iterations (int): Max iterations for the Boruta algorithm.
            random_state (int): Random state for reproducibility.
            get_model (bool): Return the Boruta model.

        Returns:
            tuple[DataFrame, DataFrame, BorutaPy]: Tuple with ranking and
                importance history. The ranking is a DataFrame with the
                metabolite as index and the ranking as values. The
                importance history is a DataFrame with the iteration
                number as rows and the metabolite as columns. If get_model
                is True, then the Boruta model is returned as well.
        """
        X = self.data_manager.data.values

        y = self.data_manager.sample_metadata[self.group].values

        rf = self.setup_random_forest(
            random_state=random_state, max_depth=max_depth, class_weight=class_weight
        )
        feat_selector = BorutaPy(
            rf,
            n_estimators=n_estimators,
            alpha=alpha,
            verbose=2,
            random_state=random_state,
            max_iter=max_iterations,
        )
        feat_selector.fit(X, y)

        importance_history = pd.DataFrame(
            feat_selector.importance_history_, index=range(max_iterations)
        )
        importance_history.columns = self.data_manager.metabolites

        ranking = pd.DataFrame(
            feat_selector.ranking_,
            columns=["rank"],
            index=self.data_manager.metabolites,
        )
        ranking.index.name = "metabolite"
        ranking = ranking.reset_index()
        if get_model:
            return (ranking, importance_history, feat_selector)
        else:
            return (ranking, importance_history)
