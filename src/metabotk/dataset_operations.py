import pandas as pd
from typing import Literal


class DatasetOperations:
    """
    Operation functions (subset, drop, sort, split)
    """

    def __init__(self, dataset):
        self.dataset = dataset

    def subset(
        self,
        what: Literal["samples", "metabolites"] = "samples",
        ids: list[str] | str = [],
    ):
        """

        Args:
            what:
            ids:

        Returns:

        """
        if what == "samples":
            return self._subset_samples(ids)
        elif what == "metabolites":
            return self._subset_metabolites(ids)

    def _subset_samples(self, samples_to_subset: list[str] | str):
        if not isinstance(samples_to_subset, list):
            samples_to_subset = list(samples_to_subset)
        remaining_data = self.dataset.data.loc[samples_to_subset]
        remaining_sample_metadata = self.dataset.sample_metadata.loc[samples_to_subset]
        return self.dataset._setup(
            data=remaining_data,
            sample_metadata=remaining_sample_metadata,
            chemical_annotation=self.dataset.chemical_annotation,
            sample_id_column=self.dataset._sample_id_column,
            metabolite_id_column=self.dataset._metabolite_id_column,
        )

    def _subset_metabolites(self, metabolites_to_subset: list[str] | str):
        """

        Args:
            metabolites_to_subset:

        Returns:

        """
        if not isinstance(metabolites_to_subset, list):
            metabolites_to_subset = list(metabolites_to_subset)

        remaining_data = self.dataset.data[metabolites_to_subset]

        remaining_chemical_annotation = self.dataset.chemical_annotation.loc[
            metabolites_to_subset
        ]
        return self.dataset._setup(
            data=remaining_data,
            sample_metadata=self.dataset.sample_metadata,
            chemical_annotation=remaining_chemical_annotation,
            sample_id_column=self.dataset._sample_id_column,
            metabolite_id_column=self.dataset._metabolite_id_column,
        )

    def drop(
        self,
        what: Literal["samples", "metabolites"] = "samples",
        ids: list[str] | str = [],
    ):
        """

        Args:
            what:
            ids:

        Returns:

        """
        if what == "samples":
            return self._drop_samples(ids)
        elif what == "metabolites":
            return self._drop_metabolites(ids)

    def _drop_samples(self, samples_to_drop: list[str] | str):
        """
        Drop specified samples from the dataset.
        Args:
            samples_to_drop:

        Returns:

        """
        if not isinstance(samples_to_drop, list):
            samples_to_drop = list(samples_to_drop)
        remaining_samples = list(
            set(self.dataset.samples).difference(set(samples_to_drop))
        )
        return self._subset_samples(remaining_samples)

    def _drop_metabolites(self, metabolites_to_drop: list[str] | str):
        """
        Drop specified metabolites from the dataset.
        Args:
            metabolites_to_drop:

        Returns:

        """
        remaining_metabolites = list(
            set(self.dataset.metabolites).difference(metabolites_to_drop)
        )
        return self._subset_metabolites(remaining_metabolites)

    def sort(
        self,
        on: Literal["samples", "metabolites"] = "samples",
        by: list[str] = [],
        ascending: bool = True,
    ):
        """

        Args:
            on:
            by:
            ascending:

        Returns:

        """
        if on == "samples":
            return self._sort_samples(by, ascending)
        elif on == "metabolites":
            return self._sort_metabolites(by, ascending)

    def _sort_samples(self, by: list[str] | str, ascending: bool = True):
        """

        Args:
            by:
            ascending:

        Returns:

        """
        sorted_ids = self.dataset.sample_metadata.sort_values(
            by=by, ascending=ascending
        ).index
        return self.subset(what="samples", ids=list(sorted_ids))

    def _sort_metabolites(self, by: list[str] | str, ascending: bool = True):
        """

        Args:
            by:
            ascending:

        Returns:

        """
        sorted_ids = self.dataset.chemical_annotation.sort_values(
            by=by, ascending=ascending
        ).index

        return self.subset(what="metabolites", ids=list(sorted_ids))

    def split(
        self,
        by: Literal["samples", "metabolites"] = "samples",
        columns: list[str] = [],
    ):
        if by == "samples":
            return self._split_by_sample_column(columns)
        elif by == "metabolites":
            return self._split_by_metabolite_column(columns)

    def _split_by_sample_column(self, sample_columns: list) -> dict:
        """

        Args:
            sample_columns:

        Returns:

        """
        split_datasets = {}
        for name, group in self.dataset.sample_metadata.groupby(by=sample_columns):
            temp_dataset = self.subset(what="samples", ids=list(group.index))
            split_datasets[name] = temp_dataset
        return split_datasets

    def _split_by_metabolite_column(self, metabolite_columns: list) -> dict:
        """

        Args:
            metabolite_columns:

        Returns:

        """
        split_dataset = {}
        for name, group in self.dataset.chemical_annotation.groupby(
            by=metabolite_columns
        ):
            temp_dataset = self.subset(what="metabolites", ids=list(group.index))
            split_dataset[name] = temp_dataset
        return split_dataset

    """
    Utility functions
    """

    def merge_sample_metadata_data(self) -> pd.DataFrame:
        """

        Returns:

        """
        # Merge sample metadata and data by matching sample IDs
        merged = self.dataset.sample_metadata.merge(
            self.dataset.data, left_index=True, right_index=True, how="inner"
        )
        return merged

    def replace_metabolite_names_in_data(self, new_column: str):
        """

        Args:
            new_column:

        Raises:
            ValueError:
        """

        if new_column not in self.dataset.chemical_annotation.columns:
            raise ValueError(f"No column named {new_column} in the metabolite metadata")

        return self.dataset._setup(
            data=self.dataset.data,
            sample_metadata=self.dataset.sample_metadata,
            chemical_annotation=self.dataset.chemical_annotation,
            sample_id_column=self.dataset._sample_id_column,
            metabolite_id_column=new_column,
        )

    def replace_sample_names_in_data(self, new_index: str):
        # Check that the column exists in the sample metadata
        if new_index not in self.dataset.sample_metadata.columns:
            raise ValueError(f"No column named {new_index} in the metabolite metadata")
        return self.dataset._setup(
            data=self.dataset.data,
            sample_metadata=self.dataset.sample_metadata,
            chemical_annotation=self.dataset.chemical_annotation,
            sample_id_column=new_index,
            metabolite_id_column=self.dataset._metabolite_id_column,
        )
