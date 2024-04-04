import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.stats import variation

def parse_input(input_data):
    '''
    Parse input data as pandas dataframe or as file path to TSV or CSV file
    '''
    if isinstance(input_data, pd.DataFrame):
        data = input_data.reset_index(drop=True)
        return data
    if isinstance(input_data, str):
        if input_data.endswith('.tsv'):
            data = pd.read_table(input_data, sep='\t').reset_index(drop=True)
        elif input_data.endswith('.csv'):
            data = pd.read_csv(input_data).reset_index(drop=True)
        return data
    raise ValueError("Input should be a Pandas DataFrame or a file path to a TSV or CSV file.")

def split_data_metadata(input_data, metabolite_info, metabolite_id_column='CHEM_ID'):
    '''
    Split metabolite abundance data from sample metadata
    '''
    #get all possible metabolite names
    metabolite_names = metabolite_info[metabolite_id_column].tolist()
    #get all columns not corresponding to a metabolite name i.e. metadata columns
    metadata_columns = [col for col in input_data.columns if col not in metabolite_names]
    #get all columns corresponding to a metabolite name
    metabolite_names= [i for i in metabolite_names if i in input_data.columns]
    #get metadata
    if len(metadata_columns) > 0:
        metadata = input_data[metadata_columns]
    else:
        metadata = None
    #get metabolite abundance data and convert to float
    data = input_data[metabolite_names]
    data=data.astype(float)
    #get list of metabolites found in the data
    metabolites = metabolite_info[metabolite_info[metabolite_id_column].isin(metabolite_names)]
    return data, metadata, metabolites

class DataClass:
    '''
    Class for working with Metabolon data
    '''
    #TODO: add support for biocrates/other providers

    def __init__(self, data, metabolite_info="config/metabolites.tsv", sample_info=None):
        '''
        Initiate the class, reading from data, metabolite info, and sample info (if sample info is not in the data file)
        '''
        parsed_data=parse_input(data)
        parsed_metabolite_info=parse_input(metabolite_info)
        #TODO for the case where sample info in different file
        #if sample_info:
        #    parsed_sample_info=parse_input(sample_info)
        #else:
        #    parsed_sample_info=None
        data, metadata, metabolites=split_data_metadata(parsed_data, metabolite_info, 'CHEM_ID')
        self.metadata=metadata
        self.data=data
        self.metabolites=metabolite_info[metabolite_info['CHEM_ID'].isin(metabolites)].reset_index(drop=True)
        self.samples = self.metadata['sample'].tolist()

    ####################################
    ###GENERAL MANIPULATION FUNCTIONS###
    ####################################

    def merge_data_metadata(self):
        '''
        Merge sample metadata with metabolite abundance data
        and return a pandas dataframe
        '''
        if self.data is None or self.metadata is None:
            raise ValueError("Data or Metadata is not available to merge.")
        merged = pd.concat([self.metadata, self.data], axis=1)
        return merged

    def save_dataframe(self, outpath):
        '''
        Save the merged sample data and metabolite abundance data to a TSV file
        '''
        df=self.merge_data_metadata()
        df.to_csv(outpath, index=False, sep='\t')

    def split_by_column(self, column):
        '''
        Split the dataset (data and metadata) in multiple independent DataClass instances
        based on the values of a column
        '''
        merged=self.merge_data_metadata()
        split_data={name:DataClass(group, self.metabolites) for name,group in merged.groupby(by=column)}
        return split_data

    def drop_unused_metabolites(self):
        '''
        Return the metabolite info for metabolites which are present in the abundance values,
         dropping all those present only in metabolite_info
        '''
        return self.metabolites[self.metabolites['CHEM_ID'].isin(self.data.columns)].reset_index(drop=True)

    def update_metabolites(self):
        '''
        Drop from the metabolite metadata those metabolites not present in the abundance data
        '''
        self.metabolites = drop_unused_metabolites()

    def check_if_same_length_of_data_and_metadata(self, input_data):
        '''
        Return True if the number of rows in the input data and in the metadata are equal
        '''
        if self.metadata is not None and len(input_data) != len(self.metadata):
            return False
        else:
            return True

    def update_data(self, new_data):
        '''
        Replace the metabolite abundance data with another pandas dataframe,
        if the number of rows corresponds with those of the sample metadata
        '''
        if isinstance(new_data, pd.DataFrame):
            if self.check_if_same_length_of_data_and_metadata(new_data):
                self.data = new_data
                self.update_metabolites()
            else:
                raise ValueError("The number of rows in new data and metadata are different.")
        else:
            raise ValueError("Input should be a Pandas DataFrame.")

    def update_metadata(self, new_data):
        '''
        Replace the sample metadata with another pandas dataframe,
        if the number of rows corresponds with those of the original metadata

        '''
        if isinstance(new_data, pd.DataFrame):
            # Check if the number of rows in new_data and metadata are equal
            if self.metadata is not None and len(new_data) != len(self.metadata):
                raise ValueError("The number of rows in new data and metadata are different.")
            self.metadata = new_data
        else:
            raise ValueError("Input should be a Pandas DataFrame.")

    def drop_rows(self, indices):
        '''
        Drop from data and metadata the input indices
        '''
        if self.data is not None and self.metadata is not None:
            self.data = self.data.drop(index=indices).reset_index(drop=True)
            self.metadata = self.metadata.drop(index=indices).reset_index(drop=True)
            self.samples = self.metadata['sample'].tolist()
        else:
            raise ValueError("Both data and metadata should be available to drop rows.")

    def drop_metabolites(self, metabolites):
        '''
        Drop the selected metabolites
        '''
        return self.data.drop(columns=metabolites)

    def extract_metabolite(self, metabolites):
        '''
        Return merged dataframe with sample metadata and abundance data for the selected metabolites
        '''
        return pd.concat([self.metadata, self.data[metabolites]], axis=1)

    def split_metabolites_by_origin(self):
        '''
        Split the dataset (data and metadata) in multiple independent DataClass instances,
        one per type of metabolite origin, each containing only the metabolites with that origin
        '''
        merged=self.merge_data_metadata()
        split_data={}
        for name,group in self.metabolites.groupby(by='ORIGIN'):
            temp_metabolites=self.metabolites[self.metabolites['ORIGIN']!=name]['CHEM_ID'].tolist()
            temp=merged.drop(columns=temp_metabolites)
            split_data[name]=DataClass(temp, self.metabolites)
        return(split_data)

    def drop_exogenous_metabolites(self):
        '''
        Drop metabolites of exogenous origin from the dataset
        '''
        self.update_data(self.drop_metabolites(self.metabolites[self.metabolites['ORIGIN']=='EXOGENOUS']['CHEM_ID']))

    #######################################
    ######OUTLIERS AND MISSING VALUES######
    #######################################

    def single_feature_outliers(self, column, threshold):
        '''
        Get outlier values present in a single feature i.e. metabolite
        See https://github.com/MRCIEU/metaboprep for method: "outliers determined as those +/- 5 IQR of the median."
        ''''
        if isinstance(column, str):
            column=self.data[column]
        median=np.nanmedian(column)
        q1 = np.nanquantile(column, 0.25)
        q3 = np.nanquantile(column, 0.75)
        iqr = q3 - q1
        cutoff = (median-(threshold*iqr), median+(threshold*iqr))
        outliers=column.where(((column<cutoff[0])|(column>cutoff[1])), other=0)
        outliers.name='outliers'
        return(outliers)

    def get_outliers_matrix(self, threshold=5, binary=False):
        '''
        Get a matrix of metabolite outliers over all dataset
        '''
        matrix=self.data.copy().apply(lambda x: self.single_feature_outliers(x, threshold=threshold))
        matrix=matrix.rename_axis(None, axis=1)
        matrix.index=self.samples
        if binary==True:
            matrix=matrix.map(lambda x: 1 if x != 0 else x)
        return matrix

    def remove_outlier_values(self, threshold=5):
        '''
        Replace outlier values with NAs in the whole dataset
        '''
        outliers=self.get_outliers_matrix(binary=True)
        outliers=outliers.reset_index(drop=True)
        self.update_data(self.data.where(outliers==0, np.nan))


    def feature_outliers(self, threshold=5):
        '''
        Return the number of outliers per feature i.e. metabolite
        '''
        matrix=self.get_outliers_matrix(threshold=threshold, binary=True)
        outliers=matrix.sum(axis=0)
        outliers.index.name='metabolite'
        outliers.name='outliers'
        outliers=outliers.reset_index()
        return outliers

    def sample_outliers(self, threshold=5):
        '''
        Return the number of outliers per sample
        '''
        matrix=self.get_outliers_matrix(threshold=threshold, binary=True)
        outliers=matrix.sum(axis=1)
        outliers.index.name='sample'
        outliers.name='outliers'
        outliers=outliers.fillna(0).astype(int)
        outliers=outliers.reset_index()
        return outliers

    def feature_missingness(self):
        '''
        Get number of missing values per feature i.e. metabolite
        '''
        missing=self.data.copy().apply(lambda x:x.isna().sum())
        missing.name='missing'
        missing.index.name='metabolite'
        missing=missing.fillna(0).astype(int)
        missing=missing.reset_index()
        return missing

    def sample_missingness(self):
        '''
        Get number of missing values per sample
        '''
        missing_per_sample=self.data.isna().sum(axis=1)
        missing_per_sample.name='missing'
        missing_per_sample.index=self.samples
        missing_per_sample.index.name='sample'
        missing_per_sample=missing_per_sample.reset_index()
        return missing_per_sample

    def drop_columns_with_missing_threshold(self, threshold=0.25, remove_also_outliers=True):
        '''
        Remove from the dataset all metabolites with a percentage of missing values
        greater than the threshold; if specified, consider also outlier values for the calculation
        '''
        if remove_also_outliers==False:
            missing=self.feature_missingness()
        else:
            missing=self.feature_missingness().set_index("metabolite")['missing'] + self.feature_outliers().set_index("metabolite")['outliers']
        missing.index.name=None
        new_data=self.drop_metabolites(list(missing[(missing/len(self.data))>threshold].index))
        new_data=new_data.rename_axis(None, axis=1)
        self.update_data(new_data)

    #########################################
    ######FEATURE LEVEL STATISTICS###########
    #########################################

    def single_feature_stats(self, metabolite):
        '''
        Get some statistics about the abundance of a single feature i.e. metabolite
        '''
        if isinstance(metabolite, str):
            desc=self.data[metabolite].describe()
            desc.name=metabolite
            cv=variation(self.data[metabolite].dropna())*100
        else:
            desc=metabolite.describe()
            desc.name=metabolite.name
            cv=variation(metabolite.dropna())*100
        desc['CV%']=cv
        return(desc)

    def feature_stats(self):
        '''
        Get some statistics about each metabolite abundance values
        '''
        stats=self.data.copy().apply(self.single_feature_stats).transpose()
        stats.index.name='metabolite'
        missingness=self.feature_missingness()
        outliers=self.feature_outliers()
        stats=stats.reset_index()
        stats=stats.merge(missingness, on='metabolite')
        stats=stats.merge(outliers, on='metabolite')
        stats['missing_and_outliers']=stats['missing']+stats['outliers']
        metabolite_info=self.metabolites[['CHEM_ID','SUPER_PATHWAY','SUB_PATHWAY','CHEMICAL_NAME','ORIGIN']]
        metabolite_info=metabolite_info.rename(columns={'CHEM_ID':'metabolite'})
        stats=stats.merge(metabolite_info, on='metabolite')
        return(stats)

    #########################################
    ######SAMPLE LEVEL STATISTICS###########
    #########################################

    def total_sum_abundance(self, include_missing=True):
        '''
        Compute the Total Sum Abundance (TSA) values for each sample,
        either on all metabolites or only on the complete ones without missing data
        '''
        if include_missing==True:
            tsa=self.data.sum(axis=1)
            tsa.name='TSA'
        else:
            tsa=self.data.dropna(how='any', axis=1).sum(axis=1)
            tsa.name='TSA_complete_only'
        tsa.index=self.samples
        tsa.index.name='sample'
        tsa = tsa.reset_index()
        return tsa

    def sample_stats(self):
        tsa=self.total_sum_abundance()
        tsa_complete=self.total_sum_abundance(include_missing=False)
        outliers=self.sample_outliers()
        missingness=self.sample_missingness()
        stats=tsa.merge(tsa_complete, on='sample')
        stats=stats.merge(missingness, on='sample')
        stats=stats.merge(outliers, on='sample')
        stats['missing_and_outliers']=stats['missing']+stats['outliers']
        stats=self.metadata.merge(stats, on='sample')
        return stats

    #########################
    ####DATA EXPLORATION#####
    #########################

    def plot_metabolite(self, metabolite, x='sample', hue=None, savepath=None):
        '''
        Plot a simple scatterplot with the metabolite abundance data on the Y axis,
        an X column (default is sample) and optionally a hue, and return the seaborn plot object
        '''
        ##TODO: check if plotting after extract_metabolite is faster than on the whole data
        #data=self.extract_metabolite(metabolite)
        plot=sns.scatterplot(data=self.data, x=x, y=metabolite, hue=hue)
        if savepath:
            plot.figure.savefig(savepath)
        return plot

    def get_pca(self, input_data=None, n_components=3, output_pca_object=False):
        if input_data is None :
            input_data = self.data
        # Check if all columns have numeric data types
        if input_data.isnull().any().any():
            print("Data contains NaN values; columns with empty values were ignored")
            input_data = input_data.dropna(axis=1)
        if not input_data.select_dtypes(include=['number']).equals(input_data):
            raise ValueError("Not all columns contain numeric data.")

        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(input_data)

        pca = PCA(n_components=n_components).fit(scaled_data)
        pca_transformed = pd.DataFrame(pca.transform(scaled_data), columns=[f'PC{i}' for i in range(1, n_components + 1)])
        pca_transformed=pd.concat([self.metadata, pca_transformed], axis=1)
        if output_pca_object==True:
            return pca, pca_transformed
        else:
            return pca_transformed

    #########################################
    ######STATISTICAL ANALYSES###############
    #########################################

    def ttest_feature(self, feature=None, column_to_split='breed'):
        '''
        Compute a simple T-test on a single metabolite
        '''
        split_data=self.split_by_column(column_to_split)
        group_1=split_data[list(split_data.keys())[0]]
        group_2=split_data[list(split_data.keys())[1]]
        t_test=ttest_ind(group_1.data[feature], group_2.data[feature])
        return(t_test)
