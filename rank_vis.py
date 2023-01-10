# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

cerv_data = pd.read_csv('data/cervical_cancer_data.csv')

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
    df: pandas DataFrame
        cleaned dataframe    
    """

    # Fill NaNs
    df['Category Type'].fillna('NA', inplace=True)

    if age==True:
        df.drop(columns=['Age'], inplace=True)

    if sex==True:
        df.drop(columns=['Sex'], inplace=True)

    # Remove Unnecessary Columns
    df.drop(columns=['Upper CI limit', 'Lower CI limit', 'Count', 'Denominator', 'Value note'], inplace=True)
    return df

df = basic_data_cleaning(cerv_data, True, True)
# can possibly add this to the cleaning as bools.
df=df.drop(columns=["Category Type", "Category"])
# part of the rank_clean function in rank graph class
df = df[df["Area Type"]=="Region"]
df.tail()
# Creates a list of area names
list_reg=[*set(df["Area Name"])]
# Selects which regions to compare
list_select=list_reg[:5]
df_select = df[df['Area Name'].isin(list_select)]
df_select.head(8)
# Changing the data type into string:
df_select = df_select.astype({'Area Name': str})
df_select.reset_index(inplace=True)
df_year = df_select
if "index" in df_year.columns:
    df_year = df_year.drop(columns=["index"])

keep = []
years = list(set(df_year['Time period']))
years
for i in years:
    df = df_year.loc[df_year['Time period']==i]
    order = df['Value'].rank(ascending=0)
    df['rank'] = [int(i) for i in order]
    keep.append(df)
keep

df_year = pd.concat(keep)
df_year.sort_values(['Area Name', 'Time period'], ascending=True,
                     inplace=True, ignore_index=True)
df_year.tail(10)

# color palette
region = list(set(df_select['Area Name']))
pal = list(sns.color_palette(palette='Spectral',
                             n_colors=len(region)).as_hex())
dict_color = dict(zip(region, pal))

# Plotting animated bar chart of each region's position:
fig = px.bar(df_year, x='Area Name', y='Value',
             color='Area Name', text='rank',
             color_discrete_map= dict_color,
             animation_frame='Time period',
             animation_group='Station code',
             range_y=[65, 80],
             labels={ 'Value': 'Proportion Screened, %'},
            )
fig.update_layout(width=1000, height=600, showlegend=False,
                  xaxis = dict(tickmode = 'linear', dtick = 1))
fig.update_traces(textfont_size=16, textangle=0)
fig.show()


class Rank_Based_Graph:
    def __init__(self, df):
        self.df = df
    
    def clean_rank(self):
        self.df = self.df[self.df["Area Type"]=="Region"]
