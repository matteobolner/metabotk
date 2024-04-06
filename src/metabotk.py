from src.classes import *
from src.utils import parse_input, split_data_from_metadata
from src.outliers import *

metabolite_info = parse_input("data/metabolite_info.tsv")
metabolite_info = MetaboliteInfo(metabolite_info)

dataset = parse_input("data/QC_norm_data_common.tsv")
data, metadata = split_data_from_metadata(
    dataset, metabolite_info.info["CHEM_ID"].astype(str).tolist()
)

metabolite_data = MetaboliteData(data)
sample_info = SampleInfo(sample_info=metadata, sample_id_column="CLIENT_IDENTIFIER")


dataset = MetaboTK(sample_info, metabolite_info, metabolite_data)

test = get_outliers_matrix(data_frame=metabolite_data.data)
