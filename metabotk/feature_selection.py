"""
This module provides feature selection methods using scikit-learn.

Currently implemented methods:

* Boruta feature selection using the BorutaPy algorithm from boruta

"""

import dill
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

    def __init__(self, data_manager):
        """
        Initiate the class

        Args:
            data_manager (DatasetManager): DatasetManager object with data to be selected
        """
        self.data_manager = data_manager

    def setup_random_forest(self, random_state, threads, max_depth, class_weight):
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
            n_jobs=threads,
            class_weight=class_weight,
            max_depth=max_depth,
            random_state=random_state,
        )
        return rf

    def boruta(
        self,
        y_column,
        threads=1,
        random_state=42,
        max_depth=None,
        class_weight="balanced",
        n_estimators="auto",
        alpha=0.01,
        max_iterations=1000,
        output_dir=None,
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
        if not y_column:
            raise ValueError("y value must be specified")
        X = self.data_manager.data.values

        y = self.data_manager.sample_metadata[y_column].values

        rf = self.setup_random_forest(
            random_state=random_state,
            threads=threads,
            max_depth=max_depth,
            class_weight=class_weight,
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
        print(feat_selector.importance_history_)
        importance_history = pd.DataFrame(
            feat_selector.importance_history_,
            index=range(len(feat_selector.importance_history_)),
        )
        importance_history.columns = self.data_manager.metabolites
        importance_history.index.name = "iteration"
        importance_history = importance_history.reset_index()

        ranking = pd.DataFrame(
            feat_selector.ranking_,
            columns=["rank"],
            index=self.data_manager.metabolites,
        )
        ranking.index.name = "metabolite"
        ranking = ranking.reset_index()

        if output_dir:
            with open(f"{output_dir}/boruta_model.pickle", "wb") as f:
                dill.dump(feat_selector, f)
            importance_history.to_csv(
                f"{output_dir}/boruta_importance_history.tsv", sep="\t", index=False
            )

            ranking.to_csv(f"{output_dir}/boruta_ranking.tsv", sep="\t", index=False)
            return ranking
        else:
            return ranking
