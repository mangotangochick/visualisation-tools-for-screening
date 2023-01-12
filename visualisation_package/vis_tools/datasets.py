'''
Contains functions for cleaning external datasets and loading built-in ones. 
One for cervical, one for bowel, one for breast cancer screening. 

Datasets originate from Health and Social Care Information Centre/Public 
Health England. 
Source: https://data.england.nhs.uk/organization/public-health-england?page=3

basic_data_cleaning: shapes the dataframes for visualisation.
load_cerv: loads data from cervical screening file from 2010 to 2016.
load_bowel: loads data from bowel screening file from 2015 to 2016.
load_breast: loads data from breast screening file from 2010 to 2016.
'''
import pandas as pd
import os 
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import data
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

package_dir = os.path.dirname(data.__file__)
print(package_dir)

def basic_data_cleaning(df, age=True, sex=True, deprivation=False):
    """
    Function for basic data cleaning of an NHS screening uptake dataset.
    It is possible to choose if to include age, sex and deprivation status. 

    Parameters
    ----------
    df: pandas DataFrame
        DataFrame containing the data to be explored.
    age: bool
        If True, then includes age information
    sex: bool
        If True, then includes sex information
    deprivation: bool
        If True, then only includes rows with deprivation deciles. 
    Returns
    -------
    df: pandas DataFrame
        data frame with unnecessary data excluded 
    """
    # Fill NaNs
    df['Category Type'].fillna('NA', inplace=True)
    
    # Dropping "Cl_L3_..." values representing types of areas.
    df = df[df['Area Code'].str.contains('E')]
    
    # Columns we want to keep. 
    keep_col = ['Area Code', 'Area Name', 'Area Type', 'Time period', 'Value']

    if deprivation==True:
        df = df[df['Category Type'].str.contains('deprivation deciles in England')]
    else:
        if age == True:
            keep_col.append('Age')
        if sex == True:
            keep_col.append('Sex')

    # Remove Unnecessary Columns
    df = df[keep_col]
    return df


def load_cerv(age=True, sex=True, deprivation=False):
    '''
    Loads data from local a file on cervical cancer screening. 
    The file includes data on the percentage of women in the resident
    population eligible for cervical cancer screening who were screened
    adequately within the years 2010 and 2016.
    ----------
    Parameters
    ----------
    age: bool
        If True, then includes age information
    sex: bool
        If True, then includes sex information
    deprivation: bool
        If True, then includes "Category type" and "Category columns", which
        describe deprivation groups.
    Returns
    -------
    cerv_data: pandas DataFrame
        cleaned dataframe    
    '''  
    filepath = os.path.join(package_dir, 'cervical_cancer_data.csv')
    cerv_data = pd.read_csv(filepath)
    cerv_data = basic_data_cleaning(cerv_data, age=age, sex=sex, 
                                     deprivation=deprivation)
    return cerv_data

def load_bowel(age=True, sex=True, deprivation=False):
    '''
    Loads data from local file on bowel cancer screening. 
    The file includes data on the percentage of people in the resident
    population eligible for bowel screening who were screened adequately
    within the years 2010 and 2016.
    ----------
    Parameters
    ----------
    age: bool
        If True, then includes age information
    sex: bool
        If True, then includes sex information
    deprivation: bool
        If True, then includes "Category type" and "Category columns", which
        describe deprivation groups.
    Returns
    -------
    bowel_data: pandas DataFrame
        cleaned dataframe    
    '''
    filepath = os.path.join(package_dir, 'bowel_cancer_data.csv')
    bowel_data = pd.read_csv(filepath)
    bowel_data = basic_data_cleaning(bowel_data, age=age, sex=sex, 
                                     deprivation=deprivation)
    return bowel_data

def load_breast(age=True, sex=True, deprivation=False):
    '''
    Loads data from local file on breast cancer screening. 
    The file includes data on the percentage of people in the resident
    population eligible for breast cancer screening who were screened
    adequately within the years 2010 and 2016.
    ----------
    Parameters
    ----------
    age: bool
        If True, then includes age information
    sex: bool
        If True, then includes sex information
    deprivation: bool
        If True, then includes "Category type" and "Category columns", which
        describe deprivation groups.
    Returns
    -------
    breast_data: pandas DataFrame
        cleaned dataframe    
    '''
    filepath = os.path.join(package_dir, 'breast_cancer_data.csv')
    breast_data = pd.read_csv(filepath)
    breast_data = basic_data_cleaning(breast_data, age=age, sex=sex, 
                                     deprivation=deprivation)
    return breast_data

def load_custom(filename=str, age=True, sex=True, deprivation=False):
    '''
    Loads data from local custom file

    If you are using your own dataset. Ensure its columns include:
    * 'Area Code', eg. 'E12000001'
    * 'Area Name', eg. 'Exeter'
    * 'Area Type', eg. 'LA'
    * 'Time period', eg. 2010
    * 'Value', eg. '77.5379545'
    * 'Age', eg. '25-64 yrs'
    * 'Sex', eg. 'Female'

    ----------
    Parameters
    ----------
    filepath: str
        The relative path for accessing the custom dataset
    age: bool
        If True, then includes age information
    sex: bool
        If True, then includes sex information
    deprivation: bool
        If True, then includes "Category type" and "Category columns", which
        describe deprivation groups.
    Returns
    -------
    breast_data: pandas DataFrame
        cleaned dataframe    
    '''
    filepath = os.path.join(package_dir, filename)
    custom_data = pd.read_csv(filepath)
    custom_data = basic_data_cleaning(custom_data, age=age, sex=sex, 
                                     deprivation=deprivation)
    return custom_data

class BasicDataExploration:

    def __init__(self, df, dep_deciles = bool):
        self.df = df
        self.dep_deciles = dep_deciles

    def explore(self):
        print(' ')
        print(f'The datatypes of the columns in the DataFrame are:\
            \n{self.df.dtypes}')
        print(' ')
        print(f'The number of null values in each column are:\
            \n{self.df.isnull().sum()}')

        # Check for any duplicated rows
        print(f'The number of duplicated rows are:\
             {self.df.duplicated().sum()}')

        # Show Area Type Frequency
        print('Below is a barplot of Area Type frequencies:')
        self.df['Area Type'].value_counts().plot.bar(figsize=(10,5))
        plt.show()

        # Generate histogram to identify outliers for the 'Value' Column
        print('Below is a histogram of the float columns:') 
        sns.histplot(self.df['Value'])
        plt.ylabel('Percentage Uptake (%)')
        plt.show()

        # Count by area name
        print('Below is a barplot overview of the area names and frequencies:') 
        area_freq = self.df.groupby(['Area Name'])['Area Name'].count()
        area_freq.plot(kind='bar', figsize =(100,5))
        plt.legend(prop={'size': 4})
        plt.xticks(rotation=90)
        plt.figure(dpi=300)
        plt.show()


        if self.dep_deciles == True:
            county_dd = self.df[self.df['Category Type'].\
                isin(["County & UA deprivation deciles in England (IMD2010)", \
                    "County & UA deprivation deciles in England (IMD2015)"])]
            district_dd = self.df[self.df['Category Type'].\
                isin(["District & UA deprivation deciles in England (IMD2010)", \
                    "District & UA deprivation deciles in England (IMD2015)"])]

            print(len(county_dd))
            print(len(district_dd))

            county_cat_yr_freq = county_dd.groupby(['Category', 'Time period'])['Time period'].count()
            county_cat_yr_freq = county_cat_yr_freq.unstack(level=0)
            county_cat_yr_freq.plot(kind='bar', figsize =(12,5), legend = 'right')
            plt.legend(prop={'size': 4})
            plt.figure(dpi=300)
            plt.show()

            district_cat_yr_freq = district_dd.groupby(['Category', 'Time period'])['Time period'].count()
            district_cat_yr_freq = district_cat_yr_freq.unstack(level=0)
            district_cat_yr_freq.plot(kind='bar', figsize =(12,5), legend = 'right')
            plt.legend(prop={'size': 4})
            plt.figure(dpi=300)
            plt.show()

