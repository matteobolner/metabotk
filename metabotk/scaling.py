class ScalingHandler:
    """
    Class for performing scaling procedures on metabolomics data.
    """

    def __init__(
        self,
        dataset_manager,
    ):
        """
        Initialize the class.
        """
        self._dataset_manager = dataset_manager

    def tsa(self, inplace=True):
        """
        Scale by dividing each metabolite value by the Total Sum Abundance (TSA) of its sample
        """
        tsa = self._dataset_manager.data.sum(axis=1).to_dict()
        scaled = self._dataset_manager.data.apply(lambda x: x / tsa[x.name], axis=1)
        if inplace:
            self._dataset_manager.data = scaled
        else:
            return scaled

    def median(self, inplace=True):
        """
        Scale by dividing each metabolite value by the median of the metabolite values across all samples
        """
        scaled = self._dataset_manager.data / self._dataset_manager.data.median()
        if inplace:
            self._dataset_manager.data = scaled
        else:
            return scaled
