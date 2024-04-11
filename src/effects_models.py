import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import dill
import os
from src.utils import create_directory

class EffectsHandler:
    """
    Class for fitting linear models to the data and obtaining residuals
    """
    def __init__(self, data_manager, formula="C(slaughter) + C(batch) + weight", models_path=None) -> None:
        """
        Initialize the class.
        """
        self.data_manager=data_manager
        self.formula=formula
        self.merged=self.data_manager.merge_sample_metadata_data()
        self.residuals=self.data_manager.data.copy()
        self.residuals.loc[:]=np.nan

    def fit_model(self, metabolite):
        model = smf.ols(f"Q('{metabolite}') ~ {self.formula}", self.merged)
        fitted_model = model.fit()
        residuals=fitted_model.resid
        return residuals, model

    def get_all_residuals(self, models_path=None):
        if models_path:
            create_directory(models_path)
        for metabolite in self.data_manager.metabolites:
            residuals, model = self.fit_model(metabolite)
            self.residuals[metabolite]=residuals
            if models_path:
                with open(f"{models_path}/{metabolite}.pickle", 'wb') as handle:
                    dill.dump(model, handle)
        return self.residuals
