from metabotk.metabolomic_dataset import MetabolomicDataset
from metabotk.dataset_manipulator import DatasetManipulator
from metabotk.dataset_io import read_excel, read_prefix, save_excel, save_prefix


class MetaboTK(MetabolomicDataset):
    def __init__(
        self,
        data,
        sample_metadata,
        chemical_annotation,
        sample_id_column="sample",
        metabolite_id_column="CHEM_ID",
    ) -> None:
        super().__init__(
            data,
            sample_metadata,
            chemical_annotation,
            sample_id_column,
            metabolite_id_column,
        )
        self.manipulator = DatasetManipulator()
        return

    def __getattr__(self, name):
        if hasattr(self.processor, name):
            processor_method = getattr(self.processor, name)

            def wrapper(*args, **kwargs):
                result = processor_method(self.data, *args, **kwargs)
                if isinstance(result, list):
                    self.data = result
                    return self
                return result

            return wrapper
        raise AttributeError(f"'Dataset' object has no attribute '{name}'")
