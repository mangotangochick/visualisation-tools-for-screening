'''
Contains functions for loading and cleaning built-in datasets. 
One for cervical, one for bowel, one for breast cancer screening. 
'''
import pandas as pd

PATH_CERV='data/cervical_cancer_data.csv'
cerv_data = pd.read_csv(PATH_CERV)        

def basic_data_cleaning(df, age=bool, sex=bool, deprivation=bool):
    """
    Function for basic data cleaning of an NHS screening uptake dataset.
    
    This function returns two cleaned datasets, one with no deprivation deciles and one with deprivation deciles

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

