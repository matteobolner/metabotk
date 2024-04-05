from src.utils import parse_input, split_data_from_metadata



class MetaboliteData:
    def __init__(self, metabolite_data):
        self.data=parse_input(metabolite_data)


class MetaboliteInfo:
    def __init__(self, metabolite_info):
        self.info=parse_input(metabolite_info)

class SampleInfo:
    def __init__(self, sample_info, sample_id_column='sample'):
        self.info=parse_input(sample_info)
        self.samples=self.info[sample_id_column]

class MetaboTK:
    def __init__(self, sample_info, metabolite_info, metabolite_data):
        self.metadata=sample_info
        self.metabolites=metabolite_info
        self.data=metabolite_data

    def merge_data_metadata(self):
        '''
        Merge sample metadata with metabolite abundance data
        and return a pandas dataframe
        '''
        if self.data is None or self.metadata is None:
            raise ValueError("Data or Metadata is not available to merge.")
        merged = pd.concat([self.metadata, self.data], axis=1)
        return merged
