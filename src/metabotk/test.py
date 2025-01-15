from metabotk.main import MetaboTK as mtk

a = mtk().io.from_excel(
    "tests/test_data/cdt_demo.xlsx", sample_id_column="PARENT_SAMPLE_NAME"
)
b = a.ops.subset(what="samples", ids=a.samples[0:10])


print(b.stats.sample_stats())
