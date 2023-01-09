# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

cerv_data = pd.read_csv('data/cervical_cancer_data.csv')

def basic_data_exploration(df, dep_deciles = bool):
    """
    Function for basic data exploration of an NHS screening uptake dataset.
    
    This function produces information on the dataset and produces multiple matplotlib plots for basic data exploration

    Parameters
    ----------
    df: pandas DataFrame
        DataFrame containing the data to be explored.
    dep_deciles: bool
        If True, then executes code that produces graphs for deprivation deciles
    
    Returns
    -------
    None: NoneType
        This function does not return a value.
    
    """
    print(' ')
    print(f'The datatypes are:\n{df.dtypes}')
    print(' ')
    print(f'The number of null values are:\n{df.isnull().sum()}')

    # Check for any duplicated rows
    print(f'Duplicated Rows:, {df.duplicated().sum()}')

    # Plot a histogram of the float columns
    float_df = df.select_dtypes(include='float')
    float_df.hist(figsize=(10,5))
    plt.show()

    # Show Area Type Frequency
    df['Area Type'].value_counts().plot.bar(figsize=(10,5))
    plt.show()

    # Generate histogram to identify outliers for the 'Value' Column
    sns.histplot(df['Value'])
    plt.ylabel('Percentage Uptake (%)')
    plt.show()

    # Count by area name
    area_freq = df.groupby(['Area Name'])['Area Name'].count()
    area_freq.plot(kind='bar', figsize =(100,5))
    plt.legend(prop={'size': 4})
    plt.xticks(rotation=90)
    plt.figure(dpi=300)
    plt.show()


    if dep_deciles == True:
        county_dd = df[df['Category Type'].isin(["County & UA deprivation deciles in England (IMD2010)", "County & UA deprivation deciles in England (IMD2015)"])]
        district_dd = df[df['Category Type'].isin(["District & UA deprivation deciles in England (IMD2010)", "District & UA deprivation deciles in England (IMD2015)"])]

        print(len(county_dd))
        print(len(district_dd))

        county_cat_yr_freq = county_dd.groupby(['Category', 'Time period'])['Time period'].count()
        county_cat_yr_freq = county_cat_yr_freq.unstack(level=0)
        county_cat_yr_freq.plot(kind='bar', figsize =(12,5), legend = 'right')
        plt.legend(prop={'size': 4})
        plt.figure(dpi=300)
        plt.show()

basic_data_exploration(df=cerv_data, dep_deciles=True)

def basic_data_cleaning(df, age=bool, sex=bool):

    """
    Function for basic data cleaning of an NHS screening uptake dataset.
    
    This function returns two cleaned datasets, one with no deprivation deciles and one with deprivation deciles

    Parameters
    ----------
    df: pandas DataFrame
        DataFrame containing the data to be explored.
    age: bool
        If True, then executes code that removes age information
    sex: bool
        If True, then executes code that removes sex information
    
    Returns
    -------
    deprived_df: pandas DataFrame
        Deprivation decile relevant rows only
    not_deprived_df: pandas DataFrame
        Geographical based rows only
    
    """

    # Fill NaNs
    df['Category Type'].fillna('NA', inplace=True)

    if age==True:
        df.drop(columns=['Age'], inplace=True)

    if sex==True:
        df.drop(columns=['Sex'], inplace=True)

    # Remove Unnecessary Columns
    df.drop(columns=['Upper CI limit', 'Lower CI limit', 'Count', 'Denominator', 'Value note'], inplace=True)

    # Split into separate DataFrames
    df_list = [group for _, group in df.groupby(df['Category Type'].str.contains('deprivation deciles in England'))]

    deprived_df = df_list[1]
    not_deprived_df = df_list[0]

    print('\nThe Location-based DataFrame is as follows: \n')
    print(not_deprived_df)
    print('\nThe Deprivation Deciles DataFrame is as follows: \n')
    print(deprived_df)

    return deprived_df, not_deprived_df

# Export DataFrames
cerv_deprived_df, cerv_data_clean = basic_data_cleaning(df=cerv_data, age=True, sex=True)
cerv_data_clean.to_pickle('cerv_data_clean.pkl')
cerv_deprived_df.to_pickle('cerv_deprived_df.pkl')