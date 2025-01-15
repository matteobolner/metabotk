"""
This module provides feature selection methods using scikit-learn.

Currently implemented methods:

* Boruta feature selection using the BorutaPy algorithm from boruta

"""

import dill
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import StratifiedKFold
from boruta_py_versioned import BorutaPy
import pandas as pd
from metabotk.utils import create_directory


class FeatureSelection:
    """
    Class for feature selection

    Attributes:
        data_manager (DatasetManager): DatasetManager object with data to be selected
        threads (int): Number of threads to use for parallel processing
        random_state (int): Random state for reproducibility
        group (str): Column name containing sample class information
    """

    def __init__(self, dataset):
        """
        Initiate the class

        Args:
            data_manager (DatasetManager): DatasetManager object with data to be selected
        """
        self.dataset = dataset

    def setup_random_forest(
        self,
        random_state,
        threads,
        max_depth,
        class_weight,
        kind="classifier",
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
        if kind == "classifier":
            rf = RandomForestClassifier(
                n_jobs=threads,
                class_weight=class_weight,
                max_depth=max_depth,
                random_state=random_state,
            )
        elif kind == "regressor":
            rf = RandomForestRegressor(
                n_jobs=threads,
                max_depth=max_depth,
                random_state=random_state,
            )
        return rf

    def boruta(
        self,
        y_column,
        kind="classifier",
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
        X = self.dataset.data.values

        y = self.dataset.sample_metadata[y_column].values

        rf = self.setup_random_forest(
            random_state=random_state,
            threads=threads,
            max_depth=max_depth,
            class_weight=class_weight,
            kind=kind,
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
            feat_selector.importance_history_,
            index=range(len(feat_selector.importance_history_)),
        )
        importance_history.columns = self.dataset.metabolites
        importance_history.index.name = "iteration"
        importance_history = importance_history.reset_index()

        ranking = pd.DataFrame(
            feat_selector.ranking_,
            columns=["rank"],
            index=self.dataset.metabolites,
        )
        ranking.index.name = "metabolite"
        ranking = ranking.reset_index()

        if output_dir:
            with open(f"{output_dir}/boruta_model.pickle", "wb") as f:
                dill.dump(feat_selector, f)
            importance_history.to_csv(
                f"{output_dir}/importance_history.tsv", sep="\t", index=False
            )

            ranking.to_csv(f"{output_dir}/ranking.tsv", sep="\t", index=False)
            return ranking
        else:
            return ranking

    def stratified_kfold(
        self,
        n_splits: int,
        stratification_column: str,
        output_dir=None,
    ) -> dict:
        """Split the dataset using a stratified approach for cross-validation.

        This function splits the dataset into n_splits folds using a stratified
        approach where the samples are split based on the values in the
        stratification_column in the sample metadata. The dataframes are saved
        to output_dir with filenames in the format of <fold_number>_train.tsv.
        The function returns a dictionary where the keys are the fold number
        and the values are the train dataframes.

        Args:
            n_splits: Number of splits to perform.
            output_dir: Directory to save dataframes to.
            stratification_column: Column in sample metadata to use for
                stratification.
        Returns:
            Dictionary with keys as fold numbers and values as the train
            dataframes.
        """
        X = self.dataset.data
        split_train = {}
        split_test = {}
        y = self.dataset.sample_metadata[stratification_column]
        skf = StratifiedKFold(n_splits=int(n_splits))
        skf_splits = skf.split(X, y)
        if output_dir:
            create_directory(output_dir)

        for fold, (train_idx, test_idx) in enumerate(skf_splits):
            foldname = fold + 1
            train_idx = X.iloc[train_idx].index
            test_idx = X.iloc[test_idx].index
            train = self.dataset.ops.subset(what="samples", ids=train_idx)
            test = self.dataset.ops.subset(what="samples", ids=test_idx)
            # train = X.iloc[train_idx]
            # test = X.iloc[test_idx]
            split_train[foldname] = train
            split_test[foldname] = test

            if output_dir:
                train.io.save_excel(f"{output_dir}/{foldname}_train.xlsx")
                test.io.save_excel(f"{output_dir}/{foldname}_test.xlsx")

        return {"training_set": split_train, "test_set": split_test}
