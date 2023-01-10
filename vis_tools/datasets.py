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

def basic_data_cleaning(df, age=bool, sex=bool, deprivation=bool):
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
        If True, then includes "Category type" and "Category columns", which
        describe deprivation groups. 
    Returns
    -------
    df: pandas DataFrame
        cleaned dataframe    
    """
    df = df.read_check('data/cervical_cancer_data.csv')

    # Fill NaNs
    df['Category Type'].fillna('NA', inplace=True)
    keep_col = ['Area Code', 'Area Name', 'Area Type', 'Time period', 'Value']
    if age==True:
        keep_col.append('Age')
    if sex==True:
        keep_col.append('Sex')
    if deprivation==True:
        keep_col.append('Category Type', 'Category')

    # Remove Unnecessary Columns
    df = df[keep_col]
    return df


def load_cerv(age=bool, sex=bool, deprivation=bool):
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
    cerv_data = pd.read_csv('data/cervical_cancer_data.csv')
    cerv_data = basic_data_cleaning(cerv_data, age=bool, sex=bool, 
                                    deprivation=bool)
    return cerv_data

def load_bowel(age=bool, sex=bool, deprivation=bool):
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
    bowel_data = pd.read_csv('data/bowel_cancer_data.csv')  
    bowel_data = basic_data_cleaning(bowel_data, age=bool, sex=bool, 
                                     deprivation=bool)
    return bowel_data

def load_breast(age=bool, sex=bool, deprivation=bool):
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
    breast_data = pd.read_csv('data/breast_cancer_data.csv')
    breast_data = basic_data_cleaning(breast_data, age=bool, sex=bool, 
                                     deprivation=bool)
    return breast_data