from metabotk.metabolomic_dataset import MetabolomicDataset
import pandas as pd
from typing import Literal
from metabotk.dataset_io import from_excel, read_excel


class DatasetManipulator:
    """
    Manipulation functions (subset, drop, sort, split)
    """

    @staticmethod
    def subset(
        dataset: MetabolomicDataset,
        what: Literal["samples", "metabolites"] = "samples",
        ids: list[str] | str = [],
    ) -> MetabolomicDataset:
        """

        Args:
            what:
            ids:

        Returns:

        """
        if what == "samples":
            return DatasetManipulator._subset_samples(dataset, ids)
        elif what == "metabolites":
            return DatasetManipulator._subset_metabolites(dataset, ids)

    @staticmethod
    def _subset_samples(
        dataset: MetabolomicDataset, samples_to_subset: list[str] | str
    ) -> MetabolomicDataset:
        if not isinstance(samples_to_subset, list):
            samples_to_subset = [samples_to_subset]
        remaining_data = dataset.data.loc[samples_to_subset]
        remaining_sample_metadata = dataset.sample_metadata.loc[samples_to_subset]
        return MetabolomicDataset._setup(
            data=remaining_data,
            sample_metadata=remaining_sample_metadata,
            chemical_annotation=dataset.chemical_annotation,
            sample_id_column=dataset._sample_id_column,
            metabolite_id_column=dataset._metabolite_id_column,
        )

    @staticmethod
    def _subset_metabolites(
        dataset: MetabolomicDataset, metabolites_to_subset: list[str] | str
    ) -> MetabolomicDataset:
        """

        Args:
            metabolites_to_subset:

        Returns:

        """
        if not isinstance(metabolites_to_subset, list):
            metabolites_to_subset = [metabolites_to_subset]

        remaining_data = dataset.data[metabolites_to_subset]

        remaining_chemical_annotation = dataset.chemical_annotation.loc[
            metabolites_to_subset
        ]
        return MetabolomicDataset._setup(
            data=remaining_data,
            sample_metadata=dataset.sample_metadata,
            chemical_annotation=remaining_chemical_annotation,
            sample_id_column=dataset._sample_id_column,
            metabolite_id_column=dataset._metabolite_id_column,
        )

    @staticmethod
    def drop(
        dataset: MetabolomicDataset,
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
            return DatasetManipulator._drop_samples(dataset, ids)
        elif what == "metabolites":
            return DatasetManipulator._drop_metabolites(dataset, ids)

    @staticmethod
    def _drop_samples(
        dataset: MetabolomicDataset, samples_to_drop: list[str] | str
    ) -> MetabolomicDataset:
        """
        Drop specified samples from the dataset.
        Args:
            samples_to_drop:

        Returns:

        """
        if not isinstance(samples_to_drop, list):
            samples_to_drop = [samples_to_drop]
        remaining_samples = list(set(dataset.samples).difference(set(samples_to_drop)))
        return DatasetManipulator._subset_samples(dataset, remaining_samples)

    @staticmethod
    def _drop_metabolites(
        dataset: MetabolomicDataset, metabolites_to_drop: list[str] | str
    ) -> MetabolomicDataset:
        """
        Drop specified metabolites from the dataset.
        Args:
            metabolites_to_drop:

        Returns:

        """
        remaining_metabolites = list(
            set(dataset.metabolites).difference(metabolites_to_drop)
        )
        return DatasetManipulator._subset_metabolites(dataset, remaining_metabolites)

    @staticmethod
    def sort(
        dataset: MetabolomicDataset,
        on: Literal["samples", "metabolites"] = "samples",
        by: list[str] = [],
        ascending: bool = True,
    ) -> MetabolomicDataset:
        """

        Args:
            on:
            by:
            ascending:

        Returns:

        """
        if on == "samples":
            return DatasetManipulator._sort_samples(dataset, by, ascending)
        elif on == "metabolites":
            return DatasetManipulator._sort_metabolites(dataset, by, ascending)

    @staticmethod
    def _sort_samples(
        dataset: MetabolomicDataset, by: list[str] | str, ascending: bool = True
    ) -> MetabolomicDataset:
        """

        Args:
            by:
            ascending:

        Returns:

        """
        dataset.sample_metadata = dataset.sample_metadata.sort_values(
            by=by, ascending=ascending
        )
        return DatasetManipulator.subset(
            dataset, what="samples", ids=list(dataset.sample_metadata.index)
        )

    @staticmethod
    def _sort_metabolites(
        dataset: MetabolomicDataset, by: list[str] | str, ascending: bool = True
    ) -> MetabolomicDataset:
        """

        Args:
            by:
            ascending:

        Returns:

        """
        dataset.chemical_annotation = dataset.chemical_annotation.sort_values(
            by=by, ascending=ascending
        )
        dataset.data = dataset.data[dataset.chemical_annotation.index]

        return DatasetManipulator.subset(
            dataset, what="metabolites", ids=list(dataset.chemical_annotation.index)
        )

    @staticmethod
    def split(
        dataset: MetabolomicDataset,
        by: Literal["samples", "metabolites"] = "samples",
        columns: list[str] = [],
    ):
        if by == "samples":
            return DatasetManipulator._split_by_sample_column(dataset, columns)
        elif by == "metabolites":
            return DatasetManipulator._split_by_metabolite_column(dataset, columns)

    @staticmethod
    def _split_by_sample_column(
        dataset: MetabolomicDataset, sample_columns: list
    ) -> dict[str, MetabolomicDataset]:
        """

        Args:
            sample_columns:

        Returns:

        """
        split_datasets = {}
        for name, group in dataset.sample_metadata.groupby(by=sample_columns):
            temp_dataset = DatasetManipulator.subset(
                dataset=dataset, what="samples", ids=list(group.index)
            )
            split_datasets[name] = temp_dataset
        return split_datasets

    @staticmethod
    def _split_by_metabolite_column(
        dataset: MetabolomicDataset, metabolite_columns: list
    ) -> dict[str, MetabolomicDataset]:
        """

        Args:
            metabolite_columns:

        Returns:

        """
        split_dataset = {}
        for name, group in dataset.chemical_annotation.groupby(by=metabolite_columns):
            temp_dataset = DatasetManipulator.subset(
                dataset=dataset, what="metabolites", ids=list(group.index)
            )
            split_dataset[name] = temp_dataset
        return split_dataset

    """
    Utility functions
    """

    @staticmethod
    def merge_sample_metadata_data(dataset: MetabolomicDataset) -> pd.DataFrame:
        """

        Returns:

        """
        # Merge sample metadata and data by matching sample IDs
        merged = dataset.sample_metadata.merge(
            dataset.data, left_index=True, right_index=True, how="inner"
        )
        return merged

    @staticmethod
    def replace_metabolite_names_in_data(
        dataset: MetabolomicDataset, new_column: str
    ) -> MetabolomicDataset:
        """

        Args:
            new_column:

        Raises:
            ValueError:
        """

        if new_column not in dataset.chemical_annotation.columns:
            raise ValueError(f"No column named {new_column} in the metabolite metadata")

        return MetabolomicDataset._setup(
            data=dataset.data,
            sample_metadata=dataset.sample_metadata,
            chemical_annotation=dataset.chemical_annotation,
            sample_id_column=dataset._sample_id_column,
            metabolite_id_column=new_column,
        )

    @staticmethod
    def replace_sample_names_in_data(dataset: MetabolomicDataset, new_index: str):
        # Check that the column exists in the sample metadata
        if new_index not in dataset.sample_metadata.columns:
            raise ValueError(f"No column named {new_index} in the metabolite metadata")
        return MetabolomicDataset._setup(
            data=dataset.data,
            sample_metadata=dataset.sample_metadata,
            chemical_annotation=dataset.chemical_annotation,
            sample_id_column=new_index,
            metabolite_id_column=dataset._metabolite_id_column,
        )
